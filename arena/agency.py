"""The "agency world" (v0.2): self/world and self/other experiments.

Adds to the v0.1 arena (see docs/preregistration_v0.2.md, section 3):
- a switchable heat lamp at the charger;
- a switch pad: any robot whose centre enters the pad toggles the lamp;
- a second, scripted robot (the "other");
- spontaneous lamp toggles and internal metabolic shocks (random events);
- extra senses: efference copy (previous action), previous consequence
  (previous reward), 8-sector thermal vision, on-pad floor sense, and the
  other robot's relative position.

Ground truth that the agent never observes is returned in `info`:
`info["self"]`, `info["world"]` and `info["events"]` (what happened, where,
what caused it, whether it affected the body).
"""
from __future__ import annotations

import math
from typing import Any

import mujoco
import numpy as np
from gymnasium import spaces

from arena.env import (
    AGENT_MASS_KG,
    AGENT_RADIUS_M,
    AGENT_Z_M,
    DEATH_PENALTY,
    MOTOR_GEAR,
    OBS_NAMES,
    SLIDE_DAMPING,
    TEMP_SCALE_C,
    HomeostaticArena,
    build_xml,
)
from arena.physiology import AMBIENT_C, HeatSource, homeostatic_drive
from arena.scenarios import Scenario

SECTOR_NAMES = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
AGENCY_OBS_NAMES: tuple[str, ...] = OBS_NAMES + (
    "prev_action_x", "prev_action_y",     # 11-12 efference copy
    "prev_reward",                        # 13    previous consequence
    *(f"thermal_{s}" for s in SECTOR_NAMES),  # 14-21 distal heat sense
    "on_pad",                             # 22    floor texture under the body
    "other_present", "other_dx", "other_dy",  # 23-25 seeing the other robot
)
OBS_INDEX = {name: i for i, name in enumerate(AGENCY_OBS_NAMES)}
THERMAL_SLICE = slice(OBS_INDEX["thermal_E"], OBS_INDEX["thermal_SE"] + 1)
SELF_MOTION_CHANNELS = ("pos_x", "pos_y", "vel_x", "vel_y", "prev_action_x",
                        "prev_action_y", "on_pad")
OTHER_CHANNELS = ("other_present", "other_dx", "other_dy")

THERMAL_RANGE_M = 3.0         # e-folding distance of the thermal "vision"
THERMAL_NOISE = 0.005
PREV_REWARD_SCALE = 20.0
BODY_AFFECTED_C = 0.5         # a lamp toggle "affects the body" if ambient changes this much


def agency() -> Scenario:
    """The agency world (pre-registered layout)."""
    return Scenario(
        name="agency",
        heat_sources=[HeatSource((-2.0, 2.0), peak_c=60.0, sigma=0.7)],   # static hot spot
        charger_xy=(3.0, 3.0),
        start_xy=(-3.0, -3.0),
        randomize_start=True,
        max_seconds=60.0,
        notes="Lamp at the charger, switch pad at the centre, scripted other robot.",
        extra={
            "lamp": HeatSource((3.0, 3.0), peak_c=60.0, sigma=0.7),
            "pad_xy": (0.0, 0.0),
            "pad_radius": 0.5,
            "other_speed": 0.6,
            "other_pad_prob": 0.5,
            "spontaneous_rate_hz": 1 / 20,
            "shock_rate_hz": 1 / 30,
            "shock_amount": 0.1,
            "start_energy_range": (0.4, 1.0),
        },
    )


class AgencyArena(HomeostaticArena):
    """HomeostaticArena plus lamp, switch pad, other robot and random events.

    Test hooks (used by scripted trials; never by agents): `set_other_action`,
    `schedule_toggle`, `schedule_shock`, `switch_enabled`, `random_events`, and
    reset options `other_xy`, `lamp_on`, `random_events`, `switch_enabled`.
    """

    def __init__(self, scenario: Scenario | str = "agency", frame_skip: int = 5,
                 physiology=None, sensor_noise: bool = True, seed: int | None = None):
        scenario = agency() if scenario == "agency" else scenario
        self.lamp: HeatSource = scenario.extra["lamp"]
        self.pad_xy: tuple[float, float] = scenario.extra["pad_xy"]
        self.pad_radius: float = scenario.extra["pad_radius"]
        super().__init__(scenario, frame_skip, physiology, sensor_noise, seed)

        low = np.concatenate([self.observation_space.low,
                              [-1, -1, -1] + [-0.1] * 8 + [0, 0, -2.5, -2.5]]).astype(np.float32)
        high = np.concatenate([self.observation_space.high,
                               [1, 1, 1] + [1.5] * 8 + [1, 1, 2.5, 2.5]]).astype(np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self._lamp_geom = self.model.geom("lamp").id

        self.lamp_on = False
        self.switch_enabled = True
        self.random_events = True
        self.events: list[dict] = []
        self.prev_action = np.zeros(2)
        self.prev_reward = 0.0
        self._on_pad = {"self": False, "other": False}
        self._other_target: tuple[float, float] | None = None
        self._forced_other_action: np.ndarray | None = None
        self._pending_toggle: str | None = None
        self._pending_shock: float | None = None

    # ----------------------------------------------------------------- model
    def _build_xml(self) -> str:
        lx, ly = self.lamp.p0
        px, py = self.pad_xy
        bodies = f"""    <geom name="pad" type="cylinder" pos="{px} {py} 0.004" size="{self.pad_radius} 0.004"
          contype="0" conaffinity="0" rgba=".3 .3 .9 .4"/>
    <geom name="lamp" type="sphere" pos="{lx} {ly} 0.05" size="{self.lamp.sigma}"
          contype="0" conaffinity="0" rgba="1 .1 .1 .35"/>
    <body name="other" pos="0 0 {AGENT_Z_M}">
      <joint name="other_x" type="slide" axis="1 0 0" damping="{SLIDE_DAMPING}"/>
      <joint name="other_y" type="slide" axis="0 1 0" damping="{SLIDE_DAMPING}"/>
      <geom name="other" type="cylinder" size="{AGENT_RADIUS_M} 0.1" mass="{AGENT_MASS_KG}"
            condim="1" rgba=".6 .3 .8 1"/>
    </body>
"""
        actuators = (
            f'    <motor name="other_mx" joint="other_x" gear="{MOTOR_GEAR}" ctrllimited="true" ctrlrange="-1 1"/>\n'
            f'    <motor name="other_my" joint="other_y" gear="{MOTOR_GEAR}" ctrllimited="true" ctrlrange="-1 1"/>\n'
        )
        return build_xml(self.scenario, self.params.charger_radius, bodies, actuators)

    # ----------------------------------------------------------------- state
    @property
    def other_xy(self) -> tuple[float, float]:
        return float(self.data.qpos[2]), float(self.data.qpos[3])

    def _heat_sources(self) -> list[HeatSource]:
        return self.scenario.heat_sources + ([self.lamp] if self.lamp_on else [])

    def _in_pad(self, xy) -> bool:
        return math.dist(xy, self.pad_xy) < self.pad_radius

    def _set_lamp(self, on: bool) -> None:
        self.lamp_on = on
        self.model.geom_rgba[self._lamp_geom, 3] = 0.35 if on else 0.05

    def _toggle_lamp(self, cause: str) -> None:
        before = self._ambient()
        self._set_lamp(not self.lamp_on)
        self.events.append({
            "type": "lamp_toggle", "cause": cause, "xy": self.lamp.p0,
            "lamp_on": self.lamp_on,
            "body_affected": abs(self._ambient() - before) > BODY_AFFECTED_C,
        })

    # ----------------------------------------------------------------- hooks
    def set_other_action(self, action) -> None:
        """Force the other robot's action (None: return to its patrol)."""
        self._forced_other_action = None if action is None else np.asarray(action, float)

    def schedule_toggle(self, cause: str = "spontaneous") -> None:
        """Toggle the lamp during the next step, as if caused by `cause`."""
        self._pending_toggle = cause

    def schedule_shock(self, amount: float | None = None) -> None:
        """Apply a metabolic shock (energy loss) during the next step."""
        self._pending_shock = self.scenario.extra["shock_amount"] if amount is None else amount

    # ----------------------------------------------------------------- other
    def _other_action(self) -> np.ndarray:
        if self._forced_other_action is not None:
            return self._forced_other_action
        pos = np.array(self.other_xy)
        if self._other_target is None or np.linalg.norm(self._other_target - pos) < 0.3:
            if self.np_random.random() < self.scenario.extra["other_pad_prob"]:
                self._other_target = np.array(self.pad_xy, dtype=float)
            else:
                lim = self.scenario.half_size - 0.5
                self._other_target = self.np_random.uniform(-lim, lim, size=2)
        delta = self._other_target - pos
        dist = np.linalg.norm(delta)
        if dist < 1e-9:
            return np.zeros(2)
        return self.scenario.extra["other_speed"] * delta / dist

    # ----------------------------------------------------------------- reset
    def _reset_world(self, options: dict) -> None:
        ex = self.scenario.extra
        lamp_on = options.get("lamp_on")
        self._set_lamp(bool(self.np_random.random() < 0.5) if lamp_on is None else bool(lamp_on))
        if "start_energy" not in options:
            options["start_energy"] = float(self.np_random.uniform(*ex["start_energy_range"]))
        other_xy = options.get("other_xy")
        if other_xy is None:
            lim = self.scenario.half_size - 0.5
            other_xy = tuple(self.np_random.uniform(-lim, lim, size=2))
        self.data.qpos[2:4] = other_xy
        self.random_events = bool(options.get("random_events", True))
        self.switch_enabled = bool(options.get("switch_enabled", True))
        self.events = []
        self.prev_action = np.zeros(2)
        self.prev_reward = 0.0
        self._other_target = None
        self._forced_other_action = None
        self._pending_toggle = None
        self._pending_shock = None

    def _sample_start(self) -> tuple[float, float]:
        """v0.1 start rule, plus: off the pad and >= 1 m from the other robot."""
        while True:
            xy = super()._sample_start()
            if not self._in_pad(xy) and math.dist(xy, self.other_xy) >= 1.0:
                return xy

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        obs, info = super().reset(seed=seed, options=options)
        # Robots placed on the pad at reset do not toggle the lamp.
        self._on_pad = {"self": self._in_pad(self.xy), "other": self._in_pad(self.other_xy)}
        return obs, info

    # ----------------------------------------------------------------- step
    def step(self, action):
        action = np.clip(np.asarray(action, dtype=np.float64).reshape(2), -1.0, 1.0)
        self.data.ctrl[:2] = action
        self.data.ctrl[2:4] = np.clip(self._other_action(), -1.0, 1.0)
        mujoco.mj_step(self.model, self.data, nstep=self.frame_skip)
        self.steps += 1
        self.events = []

        # World events: pad entries (edge-triggered), then spontaneous/manual toggles.
        for who, xy in (("self", self.xy), ("other", self.other_xy)):
            now = self._in_pad(xy)
            if now and not self._on_pad[who] and self.switch_enabled:
                self._toggle_lamp(who)
            self._on_pad[who] = now
        if self.random_events and self.np_random.random() < self.scenario.extra[
                "spontaneous_rate_hz"] * self.dt:
            self._toggle_lamp("spontaneous")
        if self._pending_toggle is not None:
            self._toggle_lamp(self._pending_toggle)
            self._pending_toggle = None

        ambient_c = self._ambient()
        on_charger = self._dist_to_charger() <= self.params.charger_radius
        self.body.step(self.dt, ambient_c, float(action @ action), on_charger)

        # Internal (body) events: metabolic shocks.
        shock = self._pending_shock
        self._pending_shock = None
        if shock is None and self.random_events and self.np_random.random() < \
                self.scenario.extra["shock_rate_hz"] * self.dt:
            shock = self.scenario.extra["shock_amount"]
        if shock is not None:
            self.body.energy = max(0.0, self.body.energy - shock)
            self.events.append({"type": "metabolic_shock", "cause": "internal",
                                "xy": self.xy, "body_affected": True, "amount": shock})

        drive = homeostatic_drive(self.body.energy, self.body.damage)
        reward = self._drive - drive
        self._drive = drive
        terminated = self.body.dead
        if terminated:
            reward -= DEATH_PENALTY
        truncated = self.steps >= self.max_steps
        self.prev_action = action
        self.prev_reward = float(reward)
        return (self._observation(ambient_c), float(reward), terminated, truncated,
                self._info(ambient_c, on_charger))

    # ----------------------------------------------------------------- senses
    def thermal_vision(self, xy=None) -> np.ndarray:
        """8 world-frame sectors; each the strongest active source in that direction
        (seen from `xy`, default: the agent's position; noise-free)."""
        x, y = self.xy if xy is None else (float(xy[0]), float(xy[1]))
        out = np.zeros(8)
        for src in self._heat_sources():
            nx, ny = src.nearest_point((x, y))
            d = math.hypot(nx - x, ny - y)
            value = (src.peak_c - AMBIENT_C) / TEMP_SCALE_C * math.exp(-d / THERMAL_RANGE_M)
            if d < 1e-6:
                np.maximum(out, value, out=out)
                continue
            k = int(((math.atan2(ny - y, nx - x) + math.pi / 8) % (2 * math.pi)) // (math.pi / 4))
            out[k] = max(out[k], value)
        return out

    def _observation(self, ambient_c: float) -> np.ndarray:
        base = super()._observation(ambient_c)
        thermal = self.thermal_vision()
        if self.sensor_noise:
            thermal = thermal + self.np_random.normal(0.0, THERMAL_NOISE, size=8)
        h = self.scenario.half_size
        ox, oy = self.other_xy
        x, y = self.xy
        extra = np.concatenate([
            self.prev_action,
            [np.clip(self.prev_reward * PREV_REWARD_SCALE, -1.0, 1.0)],
            thermal,
            [float(self._in_pad(self.xy)), 1.0, (ox - x) / h, (oy - y) / h],
        ])
        obs = np.concatenate([base, extra]).astype(np.float32)
        return np.clip(obs, self.observation_space.low, self.observation_space.high)

    def _info(self, ambient_c: float, on_charger: bool) -> dict[str, Any]:
        info = super()._info(ambient_c, on_charger)
        ox, oy = self.other_xy
        info.update({
            "lamp_on": self.lamp_on,
            "agent_on_pad": self._in_pad(self.xy),
            "other_x": ox,
            "other_y": oy,
            "other_on_pad": self._in_pad(self.other_xy),
            "events": list(self.events),
            "self": {
                "xy": self.xy,
                "velocity": (float(self.data.qvel[0]), float(self.data.qvel[1])),
                "skin_c": self.body.skin_c,
                "nociceptor": info["nociceptor"],
                "energy": self.body.energy,
                "damage": self.body.damage,
                "on_pad": self._in_pad(self.xy),
                "prev_action": tuple(self.prev_action),
                "prev_reward": self.prev_reward,
                "drive": self._drive,
            },
            "world": {
                "lamp_on": self.lamp_on,
                "lamp_xy": self.lamp.p0,
                "pad_xy": self.pad_xy,
                "charger_xy": self.scenario.charger_xy,
                "other_xy": (ox, oy),
                "other_on_pad": self._in_pad(self.other_xy),
                "ambient_c": ambient_c,
            },
        })
        return info
