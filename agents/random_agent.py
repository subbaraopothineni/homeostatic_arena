"""Random-walk control agent: smoothed random actions, no use of the observation."""
from __future__ import annotations

import math

import numpy as np


class RandomAgent:
    """Moves at constant speed along a heading that performs a random walk."""

    SPEED = 0.6
    TURN_NOISE = 0.3  # std of heading change per step (rad)

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.reset()

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self.rng = np.random.default_rng(self.seed)
        self.heading = self.rng.uniform(-math.pi, math.pi)

    def act(self, obs: np.ndarray, info: dict | None = None) -> np.ndarray:
        self.heading += self.rng.normal(0.0, self.TURN_NOISE)
        return np.array([self.SPEED * math.cos(self.heading),
                         self.SPEED * math.sin(self.heading)], dtype=np.float32)
