"""Tests for the v0.2 recurrent agent and its PPO trainer."""
import numpy as np
import pytest
import torch

from agents.recurrent import (
    EFFERENCE_CHANNELS,
    NetConfig,
    RecurrentActorCritic,
    RecurrentAgent,
    load_model,
)
from arena.agency import AgencyArena
from experiments.train_agent import TrainConfig, make_net, train

D = NetConfig().obs_dim


def test_shapes():
    net = RecurrentActorCritic()
    h = net.step(torch.zeros(3, D), net.initial_state(3))
    assert h.shape == (3, 128)
    assert net.policy(h).mean.shape == (3, 2)
    assert net.value(h).shape == (3,)
    assert net.predict_delta(h, torch.zeros(3, 2)).shape == (3, D)


def test_noeff_cannot_see_its_own_motor_commands():
    torch.manual_seed(0)
    net = RecurrentActorCritic(NetConfig(efference=False))
    o1 = torch.randn(1, D)
    o2 = o1.clone()
    o2[0, list(EFFERENCE_CHANNELS)] = torch.tensor([0.9, -0.9])
    h1, h2 = net.step(o1, net.initial_state(1)), net.step(o2, net.initial_state(1))
    assert torch.equal(h1, h2)
    assert torch.equal(net.predict_delta(h1, torch.tensor([[1.0, 0.0]])),
                       net.predict_delta(h1, torch.tensor([[-1.0, 0.5]])))
    full = RecurrentActorCritic(NetConfig(efference=True))
    assert not torch.equal(full.step(o1, full.initial_state(1)), full.step(o2, full.initial_state(1)))


def test_unroll_matches_stepwise_with_resets():
    torch.manual_seed(1)
    net = RecurrentActorCritic()
    obs = torch.randn(6, 2, D)
    starts = torch.zeros(6, 2)
    starts[3, 1] = 1.0                    # env 1 starts a new episode at t = 3
    h0 = torch.randn(2, 128)
    unrolled = net.unroll(obs, h0, starts)
    h = h0.clone()
    for t in range(6):
        h = net.step(obs[t], h * (1 - starts[t])[:, None])
        assert torch.allclose(unrolled[t], h)
    fresh = net.step(obs[3, 1:2], net.initial_state(1))
    assert torch.allclose(unrolled[3, 1:2], fresh)          # memory really was reset


def test_agent_wrapper():
    env = AgencyArena(seed=0)
    agent = RecurrentAgent(make_net("FULL", 0))
    obs, info = env.reset()
    for _ in range(50):
        a = agent.act(obs, info)
        assert a.shape == (2,) and np.all(np.abs(a) <= 1)
        pred = agent.predict_next(a)
        assert pred.shape == (D,)
        obs, _, term, trunc, info = env.step(a)
    agent.reset()
    assert torch.count_nonzero(agent.h) == 0


def test_untrained_is_seed_determined():
    a, log = train("UNTRAINED", 3, TrainConfig())
    b, _ = train("UNTRAINED", 3, TrainConfig())
    assert log == []
    for pa, pb in zip(a.parameters(), b.parameters()):
        assert torch.equal(pa, pb)


def test_ppo_smoke_run_consistency_and_save_load(tmp_path):
    cfg = TrainConfig(total_steps=2 * 2 * 16, n_envs=2, rollout=16, minibatches=2)
    path = tmp_path / "FULL_seed0.pt"
    net, log = train("FULL", 0, cfg, out_path=path, verbose=False)
    assert len(log) == 2
    # Before the first optimiser step the recomputed log-probs equal the stored ones.
    assert all(row["ratio_check"] < 1e-5 for row in log)
    assert all(np.isfinite(row["fwd_loss"]) for row in log)
    loaded, ckpt = load_model(path)
    assert ckpt["variant"] == "FULL" and len(ckpt["log"]) == 2
    x = torch.randn(1, D)
    assert torch.allclose(loaded.step(x, loaded.initial_state(1)), net.step(x, net.initial_state(1)))
    assert path.with_suffix(".csv").exists()


def test_nofwd_sets_prediction_weight_to_zero():
    cfg = TrainConfig(total_steps=16 * 2, n_envs=2, rollout=16, minibatches=2)
    torch.manual_seed(0)
    net, _ = train("NOFWD", 0, cfg, verbose=False)
    fresh = make_net("NOFWD", 0)
    # Only the forward model is untouched by training when its loss weight is 0.
    for (name, p), p0 in zip(net.named_parameters(), fresh.parameters()):
        if name.startswith("forward_model"):
            assert torch.equal(p, p0), name
    assert cfg.fwd_coef == 0.0
