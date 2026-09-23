"""MuJoCo + Gymnasium environment: a disc-shaped body in a walled arena with heat
sources and a charger.

The only reward is homeostatic drive reduction (Keramati & Gutkin, 2014): the
decrease of the distance between the internal state (energy, damage) and its
setpoints. The environment never rewards "avoid heat" or "reach the charger"
directly.
"""
from __future__ import annotations

import math
from typing import Any

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

from arena.physiology import (
    AMBIENT_C,
    BodyState,
    PhysiologyParams,
    ambient_temperature,
    homeostatic_drive,
    nociceptor_rate,
)
from arena.scenarios import SCENARIOS, Scenario

OBS_NAMES: tuple[str, ...] = (
    "pos_x",         # 0  proprioception: position / half_size
    "pos_y",         # 1
    "vel_x",         # 2  proprioception: velocity / 2
    "vel_y",         # 3
    "ambient_temp",  # 4  thermoreceptors sensing radiant heat: (T - 25) / 35
    "skin_temp",     # 5  skin thermoreceptors: (T_skin - 25) / 35
    "nociceptor",    # 6  heat nociceptors: nociceptor_rate(T_skin)
    "beacon",        # 7  olfaction / chemical gradient: exp(-dist_to_charger / 4)
    "touch",         # 8  mechanoreceptors: min(contact_force / 20 N, 1)
    "energy",        # 9  interoception
    "damage",        # 10 interoception
)

TIMESTEP_S = 0.01          # MuJoCo integration step
AGENT_RADIUS_M = 0.25
AGENT_MASS_KG = 1.0
SLIDE_DAMPING = 2.5        # N s / m
MOTOR_GEAR = 5.0           # N at ctrl = 1; terminal speed = gear / damping = 2 m/s
AGENT_Z_M = 0.15           # body height; the agent never touches the floor
WALL_HALF_THICKNESS_M = 0.1
WALL_HALF_HEIGHT_M = 0.3
TEMP_SCALE_C = 35.0        # (T - 25) / 35 maps 25..60 C to 0..1
TEMP_NOISE_C = 0.1
BEACON_LENGTH_M = 4.0
BEACON_NOISE = 0.002
TOUCH_SCALE_N = 20.0
VEL_SCALE = MOTOR_GEAR / SLIDE_DAMPING  # terminal speed (m/s) at ctrl = 1
DEATH_PENALTY = 1.0
START_MAX_AMBIENT_C = 30.0     # random starts must be cooler than this ...
START_MIN_CHARGER_DIST_M = 2.0  # ... and at least this far from the charger


def build_xml(scenario: Scenario, charger_radius: float = 0.6) -> str:
    """MJCF for the scenario. Heat sources and charger are visual-only geoms."""
    h = scenario.half_size
    t = WALL_HALF_THICKNESS_M
    zh = WALL_HALF_HEIGHT_M
    walls = [
        ("wall_e", (h + t, 0.0), (t, h + 2 * t)),
        ("wall_w", (-h - t, 0.0), (t, h + 2 * t)),
        ("wall_n", (0.0, h + t), (h + 2 * t, t)),
        ("wall_s", (0.0, -h - t), (h + 2 * t, t)),
    ]
    wall_xml = "\n".join(
        f'    <geom name="{n}" type="box" pos="{x} {y} {zh}" size="{sx} {sy} {zh}" '
        f'condim="1" rgba=".5 .5 .5 1"/>'
        for n, (x, y), (sx, sy) in walls
    )
    heat_xml = []
    for i, src in enumerate(scenario.heat_sources):
        vis = 'contype="0" conaffinity="0" rgba="1 .35 0 .35"'
        if src.p1 is None:
            heat_xml.append(f'    <geom name="heat_{i}" type="sphere" '
                            f'pos="{src.p0[0]} {src.p0[1]} 0" size="{src.sigma}" {vis}/>')
        else:
            heat_xml.append(f'    <geom name="heat_{i}" type="capsule" '
                            f'fromto="{src.p0[0]} {src.p0[1]} 0 {src.p1[0]} {src.p1[1]} 0" '
                            f'size="{src.sigma}" {vis}/>')
    cx, cy = scenario.charger_xy
    return f"""
<mujoco model="homeostatic_arena_{scenario.name}">
  <option timestep="{TIMESTEP_S}"/>
  <worldbody>
    <light pos="0 0 10" dir="0 0 -1" directional="true"/>
    <geom name="floor" type="plane" size="{h} {h} 0.1" rgba=".92 .92 .92 1"
          contype="0" conaffinity="0"/>
{wall_xml}
{chr(10).join(heat_xml)}
    <geom name="charger" type="cylinder" pos="{cx} {cy} 0.005" size="{charger_radius} 0.005"
          contype="0" conaffinity="0" rgba="0 .8 .2 .5"/>
    <body name="agent" pos="0 0 {AGENT_Z_M}">
      <joint name="slide_x" type="slide" axis="1 0 0" damping="{SLIDE_DAMPING}"/>
      <joint name="slide_y" type="slide" axis="0 1 0" damping="{SLIDE_DAMPING}"/>
      <geom name="agent" type="cylinder" size="{AGENT_RADIUS_M} 0.1" mass="{AGENT_MASS_KG}"
            condim="1" rgba=".2 .4 .9 1"/>
      <site name="touch_site" type="cylinder" size="{AGENT_RADIUS_M + 0.02} 0.12"
            rgba="0 0 0 0"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="motor_x" joint="slide_x" gear="{MOTOR_GEAR}" ctrllimited="true" ctrlrange="-1 1"/>
    <motor name="motor_y" joint="slide_y" gear="{MOTOR_GEAR}" ctrllimited="true" ctrlrange="-1 1"/>
  </actuator>
  <sensor>
    <touch name="touch" site="touch_site"/>
  </sensor>
</mujoco>
"""


class HomeostaticArena(gym.Env):
    """Gymnasium environment; see OBS_NAMES for the 11-dimensional observation.

    Action: desired force direction and magnitude, Box(-1, 1, shape=(2,)).
    Reward: previous_drive - current_drive, minus DEATH_PENALTY on death.
    """

    metadata = {"render_modes": []}

    def __init__(self, scenario: Scenario | str = "foraging", frame_skip: int = 5,
                 physiology: PhysiologyParams | None = None, sensor_noise: bool = True,
                 seed: int | None = None):
        super().__init__()
        self.scenario = SCENARIOS[scenario]() if isinstance(scenario, str) else scenario
        self.frame_skip = frame_skip
        self.params = physiology if physiology is not None else PhysiologyParams()
        self.sensor_noise = sensor_noise

        self.model = mujoco.MjModel.from_xml_string(
            build_xml(self.scenario, self.params.charger_radius))
        self.data = mujoco.MjData(self.model)
        self.dt = TIMESTEP_S * frame_skip
        self.max_steps = int(round(self.scenario.max_seconds / self.dt))
        self._touch_adr = int(self.model.sensor("touch").adr[0])

        # Bounds are generous; observations are clipped into them.
        low = np.array([-1.5, -1.5, -5, -5, -1, -1, 0, -0.1, 0, 0, 0], dtype=np.float32)
        high = np.array([1.5, 1.5, 5, 5, 3, 3, 1, 1.1, 1, 1, 1], dtype=np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32)

        self._pending_seed = seed
        self.body = BodyState(params=self.params)
        self.steps = 0
        self._drive = 0.0

    # ----------------------------------------------------------------- helpers
    @property
    def xy(self) -> tuple[float, float]:
        return float(self.data.qpos[0]), float(self.data.qpos[1])

    def _ambient(self) -> float:
        return ambient_temperature(self.xy, self.scenario.heat_sources)

    def _dist_to_charger(self) -> float:
        return math.dist(self.xy, self.scenario.charger_xy)

    def _touch_force(self) -> float:
        return float(self.data.sensordata[self._touch_adr])

    def _sample_start(self) -> tuple[float, float]:
        """Uniform start that is cool and not next to the charger."""
        lim = self.scenario.half_size - 0.5
        for _ in range(10_000):
            xy = tuple(self.np_random.uniform(-lim, lim, size=2))
            if (ambient_temperature(xy, self.scenario.heat_sources) < START_MAX_AMBIENT_C
                    and math.dist(xy, self.scenario.charger_xy) >= START_MIN_CHARGER_DIST_M):
                return float(xy[0]), float(xy[1])
        raise RuntimeError("could not sample a valid start position")

    def _observation(self, ambient_c: float) -> np.ndarray:
        if self.sensor_noise:
            amb_noise, skin_noise = self.np_random.normal(0.0, TEMP_NOISE_C, size=2)
            beacon_noise = self.np_random.normal(0.0, BEACON_NOISE)
        else:
            amb_noise = skin_noise = beacon_noise = 0.0
        h = self.scenario.half_size
        x, y = self.xy
        obs = np.array([
            x / h,
            y / h,
            self.data.qvel[0] / VEL_SCALE,
            self.data.qvel[1] / VEL_SCALE,
            (ambient_c + amb_noise - AMBIENT_C) / TEMP_SCALE_C,
            (self.body.skin_c + skin_noise - AMBIENT_C) / TEMP_SCALE_C,
            nociceptor_rate(self.body.skin_c),
            math.exp(-self._dist_to_charger() / BEACON_LENGTH_M) + beacon_noise,
            min(self._touch_force() / TOUCH_SCALE_N, 1.0),
            self.body.energy,
            self.body.damage,
        ], dtype=np.float32)
        return np.clip(obs, self.observation_space.low, self.observation_space.high)

    def _info(self, ambient_c: float, on_charger: bool) -> dict[str, Any]:
        x, y = self.xy
        return {
            "t": self.steps * self.dt,
            "x": x,
            "y": y,
            "ambient_c": ambient_c,
            "skin_c": self.body.skin_c,
            "nociceptor": nociceptor_rate(self.body.skin_c),
            "energy": self.body.energy,
            "damage": self.body.damage,
            "damage_taken": self.body.damage_taken,
            "on_charger": on_charger,
            "touch": self._touch_force(),  # raw contact force (N)
            "drive": self._drive,
        }

    # ------------------------------------------------------------- gym API
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        if seed is None and self._pending_seed is not None:
            seed = self._pending_seed
        self._pending_seed = None
        super().reset(seed=seed)
        options = options or {}

        mujoco.mj_resetData(self.model, self.data)
        if options.get("start_xy") is not None:
            start = options["start_xy"]
        elif self.scenario.randomize_start:
            start = self._sample_start()
        else:
            start = self.scenario.start_xy
        self.data.qpos[:2] = start
        mujoco.mj_forward(self.model, self.data)

        energy = float(options.get("start_energy", self.scenario.start_energy))
        ambient_c = self._ambient()
        self.body = BodyState(skin_c=ambient_c, energy=energy, params=self.params)
        self.steps = 0
        self._drive = homeostatic_drive(self.body.energy, self.body.damage)
        on_charger = self._dist_to_charger() <= self.params.charger_radius
        return self._observation(ambient_c), self._info(ambient_c, on_charger)

    def step(self, action):
        action = np.clip(np.asarray(action, dtype=np.float64).reshape(2), -1.0, 1.0)
        self.data.ctrl[:] = action
        mujoco.mj_step(self.model, self.data, nstep=self.frame_skip)
        self.steps += 1

        ambient_c = self._ambient()
        on_charger = self._dist_to_charger() <= self.params.charger_radius
        self.body.step(self.dt, ambient_c, float(action @ action), on_charger)

        drive = homeostatic_drive(self.body.energy, self.body.damage)
        reward = self._drive - drive
        self._drive = drive
        terminated = self.body.dead
        if terminated:
            reward -= DEATH_PENALTY
        truncated = self.steps >= self.max_steps
        return (self._observation(ambient_c), float(reward), terminated, truncated,
                self._info(ambient_c, on_charger))
