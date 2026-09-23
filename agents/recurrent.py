"""Recurrent learning agent (v0.2): actor-critic with a built-in forward model.

Architecture (see docs/preregistration_v0.2.md, section 4):

    observation -> MLP encoder -> GRU (memory) -> policy (Gaussian) and value
                                              +-> forward model: (GRU state, action)
                                                  -> predicted next observation

The policy and value are trained with PPO on the homeostatic drive-reduction
reward only. The forward model is trained self-supervised to predict the next
observation; nobody ever tells the agent what caused an event.

Variants: FULL; NOEFF (efference-copy inputs - the previous-action channels and
the forward model's action input - always zero); NOFWD (prediction loss weight
0); UNTRAINED (random weights).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import torch
from torch import nn

from arena.agency import AGENCY_OBS_NAMES, OBS_INDEX

VARIANTS = ("FULL", "NOEFF", "NOFWD", "UNTRAINED")
EFFERENCE_CHANNELS = (OBS_INDEX["prev_action_x"], OBS_INDEX["prev_action_y"])


@dataclass
class NetConfig:
    obs_dim: int = len(AGENCY_OBS_NAMES)
    act_dim: int = 2
    hidden: int = 128
    efference: bool = True        # False for NOEFF
    init_log_std: float = -0.5


class RecurrentActorCritic(nn.Module):
    def __init__(self, config: NetConfig = NetConfig()):
        super().__init__()
        self.config = config
        h, d, a = config.hidden, config.obs_dim, config.act_dim
        self.encoder = nn.Sequential(nn.Linear(d, h), nn.Tanh(), nn.Linear(h, h), nn.Tanh())
        self.gru = nn.GRUCell(h, h)
        self.policy_mean = nn.Linear(h, a)
        self.log_std = nn.Parameter(torch.full((a,), config.init_log_std))
        self.value_head = nn.Linear(h, 1)
        self.forward_model = nn.Sequential(nn.Linear(h + a, h), nn.Tanh(), nn.Linear(h, d))
        mask = torch.ones(d)
        if not config.efference:
            mask[list(EFFERENCE_CHANNELS)] = 0.0
        self.register_buffer("input_mask", mask)
        nn.init.orthogonal_(self.policy_mean.weight, gain=0.01)
        nn.init.zeros_(self.policy_mean.bias)

    def initial_state(self, batch: int) -> torch.Tensor:
        return torch.zeros(batch, self.config.hidden)

    def step(self, obs: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        """Update the memory with one observation; returns the new GRU state."""
        return self.gru(self.encoder(obs * self.input_mask), h)

    def policy(self, h: torch.Tensor) -> torch.distributions.Normal:
        return torch.distributions.Normal(self.policy_mean(h), self.log_std.exp())

    def value(self, h: torch.Tensor) -> torch.Tensor:
        return self.value_head(h).squeeze(-1)

    def predict_delta(self, h: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Forward model: predicted o(t+1) - o(t) given memory h(t) and action a(t)."""
        if not self.config.efference:
            action = torch.zeros_like(action)
        return self.forward_model(torch.cat([h, action], dim=-1))

    def unroll(self, obs: torch.Tensor, h0: torch.Tensor, starts: torch.Tensor):
        """Run the GRU over a [T, B, D] sequence; memory is reset where starts[t] == 1
        (the first step of a new episode). Returns GRU states [T, B, H]."""
        h, states = h0, []
        for t in range(obs.shape[0]):
            h = h * (1.0 - starts[t]).unsqueeze(-1)
            h = self.step(obs[t], h)
            states.append(h)
        return torch.stack(states)


def save_model(net: RecurrentActorCritic, path, variant: str, seed: int, log: list[dict],
               train_config: dict) -> None:
    torch.save({"state_dict": net.state_dict(), "net_config": asdict(net.config),
                "variant": variant, "seed": seed, "log": log, "train_config": train_config},
               path)


def load_model(path) -> tuple[RecurrentActorCritic, dict]:
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    net = RecurrentActorCritic(NetConfig(**ckpt["net_config"]))
    net.load_state_dict(ckpt["state_dict"])
    net.eval()
    return net, ckpt


class RecurrentAgent:
    """Wraps a trained network with the common agent interface, and exposes its
    memory state and forward-model predictions for the tests."""

    def __init__(self, net: RecurrentActorCritic, deterministic: bool = True,
                 seed: int | None = None):
        self.net = net
        self.deterministic = deterministic
        self.rng = torch.Generator().manual_seed(0 if seed is None else seed)
        self.reset()

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.rng.manual_seed(seed)
        self.h = self.net.initial_state(1)
        self.last_obs: np.ndarray | None = None

    @torch.no_grad()
    def observe(self, obs: np.ndarray) -> np.ndarray:
        """Feed one observation into memory; returns the GRU state (for probes)."""
        self.last_obs = np.asarray(obs, dtype=np.float32)
        self.h = self.net.step(torch.from_numpy(self.last_obs)[None], self.h)
        return self.h[0].numpy().copy()

    @torch.no_grad()
    def choose_action(self) -> np.ndarray:
        dist = self.net.policy(self.h)
        a = dist.mean
        if not self.deterministic:
            a = a + dist.stddev * torch.randn(a.shape, generator=self.rng)
        return np.clip(a[0].numpy(), -1.0, 1.0).astype(np.float32)

    @torch.no_grad()
    def predict_next(self, action) -> np.ndarray:
        """The agent's prediction of the next observation if it executes `action`."""
        a = torch.as_tensor(np.asarray(action, dtype=np.float32))[None]
        return self.last_obs + self.net.predict_delta(self.h, a)[0].numpy()

    def act(self, obs: np.ndarray, info: dict | None = None) -> np.ndarray:
        self.observe(obs)
        return self.choose_action()
