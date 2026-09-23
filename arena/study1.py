"""Training world for Study 1b: a learning agent on the Study 1 sentience markers.

Each episode is, with equal probability, the v0.1 foraging world or the v0.1
trade-off world with a start energy drawn uniformly from [0.05, 1.0], so the
agent meets both situations the markers probe. Observations are the v0.1
11-channel observations; the reward is the same drive reduction.
"""
from __future__ import annotations

import gymnasium as gym
import numpy as np

from arena.env import HomeostaticArena
from arena.scenarios import foraging, tradeoff

TRADEOFF_ENERGY_RANGE = (0.05, 1.0)


class Study1Arena(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, seed: int | None = None):
        super().__init__()
        self.rng = np.random.default_rng(seed)
        self.envs = {"foraging": HomeostaticArena(foraging(), seed=seed),
                     "tradeoff": HomeostaticArena(tradeoff(), seed=None if seed is None else seed + 7)}
        self.observation_space = self.envs["foraging"].observation_space
        self.action_space = self.envs["foraging"].action_space
        self.dt = self.envs["foraging"].dt
        self.current = self.envs["foraging"]

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        name = "foraging" if self.rng.random() < 0.5 else "tradeoff"
        self.current = self.envs[name]
        opts = dict(options or {})
        if name == "tradeoff" and "start_energy" not in opts:
            opts["start_energy"] = float(self.rng.uniform(*TRADEOFF_ENERGY_RANGE))
        return self.current.reset(seed=seed, options=opts)

    def step(self, action):
        return self.current.step(action)
