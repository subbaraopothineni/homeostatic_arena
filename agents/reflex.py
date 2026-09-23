"""Hard-wired reflex agents: the key control condition for the marker tests.

No learning and no memory beyond the previous step (plus a refractory counter).
If such an agent passes a marker, that marker cannot on its own discriminate
between a reflex arc and a more complex architecture.

Rules, in priority order:
1. Withdrawal (hard veto): reverse heading and hold it for a refractory period.
   - "nociceptive": triggered by the nociceptor signal only (the agent has to
     be heated before it withdraws), like a spinal withdrawal reflex.
   - "thermotactic": also triggered when the ambient temperature is above 35 C
     and rising, i.e. a reversal on a rising thermal gradient, as in the
     noxious-heat avoidance of C. elegans (Wittenburg & Baumeister, 1999, PNAS).
2. Wall contact: turn by a random angle in [pi/2, 3pi/2].
3. Foraging (energy < 0.6): run-and-tumble on the beacon, like E. coli
   chemotaxis (Berg & Brown, 1972, Nature): tumble with p = 0.5 whenever the
   beacon decreased since the last step, otherwise keep running.
4. Wander: heading random walk.
"""
from __future__ import annotations

import math

import numpy as np

from arena.env import OBS_NAMES, TEMP_SCALE_C
from arena.physiology import AMBIENT_C

_I = {name: i for i, name in enumerate(OBS_NAMES)}
MODES = ("nociceptive", "thermotactic")


class ReflexAgent:
    """Reflex controller that moves at constant speed along a heading angle."""

    SPEED = 0.8
    NOCICEPTOR_TRIGGER = 0.1
    THERMAL_TRIGGER_C = 35.0
    REFRACTORY_STEPS = 10
    FORAGE_BELOW_ENERGY = 0.6
    TUMBLE_PROB = 0.5
    REVERSE_NOISE = 0.2  # rad, added to the pi reversal
    RUN_NOISE = 0.1      # rad per step while running up the beacon gradient

    def __init__(self, mode: str = "nociceptive", seed: int | None = None,
                 wander_noise: float = 0.3):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
        self.mode = mode
        self.seed = seed
        self.wander_noise = wander_noise
        self.reset()

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self.rng = np.random.default_rng(self.seed)
        self.heading = self.rng.uniform(-math.pi, math.pi)
        self.refractory = 0
        self.prev_ambient_c: float | None = None
        self.prev_beacon: float | None = None
        self.last_rule = "none"   # which rule fired on the last step (for logging)

    def withdrawal_triggered(self, nociceptor: float, ambient_c: float) -> bool:
        """Does the current sensory input trigger the withdrawal reflex?"""
        if nociceptor > self.NOCICEPTOR_TRIGGER:
            return True
        if self.mode == "thermotactic" and self.prev_ambient_c is not None:
            return ambient_c > self.prev_ambient_c and ambient_c > self.THERMAL_TRIGGER_C
        return False

    def act(self, obs: np.ndarray, info: dict | None = None) -> np.ndarray:
        """Choose an action from the observation only (`info` is ignored)."""
        nociceptor = float(obs[_I["nociceptor"]])
        ambient_c = float(obs[_I["ambient_temp"]]) * TEMP_SCALE_C + AMBIENT_C
        beacon = float(obs[_I["beacon"]])
        touch = float(obs[_I["touch"]])
        energy = float(obs[_I["energy"]])

        if self.refractory > 0:
            self.refractory -= 1
            self.last_rule = "refractory"
        elif self.withdrawal_triggered(nociceptor, ambient_c):
            self.heading += math.pi + self.rng.normal(0.0, self.REVERSE_NOISE)
            self.refractory = self.REFRACTORY_STEPS
            self.last_rule = "withdraw"
        elif touch > 0.0:
            self.heading += self.rng.uniform(math.pi / 2, 3 * math.pi / 2)
            self.last_rule = "wall"
        elif energy < self.FORAGE_BELOW_ENERGY:
            if (self.prev_beacon is not None and beacon < self.prev_beacon
                    and self.rng.random() < self.TUMBLE_PROB):
                self.heading = self.rng.uniform(-math.pi, math.pi)
                self.last_rule = "tumble"
            else:
                self.heading += self.rng.normal(0.0, self.RUN_NOISE)
                self.last_rule = "run"
        else:
            self.heading += self.rng.normal(0.0, self.wander_noise)
            self.last_rule = "wander"

        self.heading = math.remainder(self.heading, 2 * math.pi)
        self.prev_ambient_c = ambient_c
        self.prev_beacon = beacon
        return np.array([self.SPEED * math.cos(self.heading),
                         self.SPEED * math.sin(self.heading)], dtype=np.float32)
