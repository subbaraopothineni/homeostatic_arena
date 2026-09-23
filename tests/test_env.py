"""Tests for the MuJoCo/Gymnasium environment."""
import math
import warnings

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from arena.env import AGENT_RADIUS_M, OBS_NAMES, HomeostaticArena
from arena.physiology import AMBIENT_C, ambient_temperature, homeostatic_drive
from arena.scenarios import foraging, tradeoff

FAR_START = (-3.0, -3.0)   # cool, far from both hot spots and the charger


def run(env, action, n_steps):
    out = None
    for _ in range(n_steps):
        out = env.step(np.asarray(action, dtype=np.float32))
        if out[2] or out[3]:
            break
    return out


@pytest.mark.parametrize("scenario", ["foraging", "tradeoff"])
def test_check_env(scenario):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        check_env(HomeostaticArena(scenario, seed=0))
    # Only the "no render modes" notice is acceptable.
    relevant = [str(w.message) for w in caught if "render" not in str(w.message).lower()]
    assert relevant == []


def test_observation_shape_and_finite_over_random_steps():
    env = HomeostaticArena("foraging", seed=1)
    env.action_space.seed(1)
    obs, info = env.reset()
    assert obs.shape == (11,) and len(OBS_NAMES) == 11 and obs.dtype == np.float32
    for _ in range(500):
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        assert obs.shape == (11,)
        assert np.all(np.isfinite(obs)) and math.isfinite(reward)
        assert env.observation_space.contains(obs)
        if terminated or truncated:
            obs, info = env.reset()


def test_info_keys():
    env = HomeostaticArena("foraging", seed=0)
    _, info = env.reset()
    for key in ["t", "x", "y", "ambient_c", "skin_c", "nociceptor", "energy", "damage",
                "on_charger", "touch", "drive"]:
        assert key in info


def test_terminal_speed_about_2_m_per_s():
    env = HomeostaticArena("foraging", sensor_noise=False)
    env.reset(seed=0, options={"start_xy": (-4.0, -3.0)})
    run(env, [1.0, 0.0], 60)  # 3 s: long enough to settle, short of the far wall
    assert env.data.qvel[0] == pytest.approx(2.0, abs=0.05)
    assert abs(env.data.qvel[1]) < 1e-6


def test_zero_action_does_not_move_and_drains_energy():
    env = HomeostaticArena("foraging")
    env.reset(seed=0, options={"start_xy": FAR_START})
    n = int(round(20.0 / env.dt))
    obs, _, terminated, truncated, info = run(env, [0.0, 0.0], n)
    assert not terminated and not truncated
    assert math.dist((info["x"], info["y"]), FAR_START) < 1e-9
    assert 1.0 - info["energy"] == pytest.approx(0.24, abs=1e-6)
    assert info["damage"] == 0.0


def test_constant_push_reaches_east_wall_and_stops():
    env = HomeostaticArena("foraging")
    half = env.scenario.half_size
    env.reset(seed=0, options={"start_xy": FAR_START})
    max_x = -np.inf
    for _ in range(int(8.0 / env.dt)):
        obs, *_ = env.step(np.array([1.0, 0.0], dtype=np.float32))
        max_x = max(max_x, env.data.qpos[0])
    inner_face = half - AGENT_RADIUS_M
    assert max_x < inner_face + 0.02          # does not pass through (soft contact only)
    assert env.data.qpos[0] > inner_face - 0.02
    assert abs(env.data.qvel[0]) < 0.01       # stopped
    assert obs[OBS_NAMES.index("touch")] > 0.0


def test_heat_source_centre_damages_and_kills():
    env = HomeostaticArena("foraging")
    centre = env.scenario.heat_sources[0].p0
    env.reset(seed=0, options={"start_xy": centre})
    damages = []
    terminated = False
    reward = 0.0
    for _ in range(200):
        _, reward, terminated, _, info = env.step(np.zeros(2, dtype=np.float32))
        damages.append(info["damage"])
        if terminated:
            break
    assert terminated and info["damage"] >= 1.0
    assert damages[0] > 0.0 or damages[1] > 0.0
    assert info["nociceptor"] > 0.99
    assert reward < -1.0                      # death penalty applied


def test_charger_raises_energy():
    env = HomeostaticArena("foraging")
    env.reset(seed=0, options={"start_xy": env.scenario.charger_xy, "start_energy": 0.5})
    _, _, _, _, info = run(env, [0.0, 0.0], int(round(1.0 / env.dt)))
    assert info["on_charger"]
    assert info["energy"] == pytest.approx(0.5 + (0.25 - 0.012) * 1.0, abs=1e-6)


def test_truncation_at_max_seconds():
    env = HomeostaticArena(tradeoff(0.9))
    env.reset(seed=0, options={"start_xy": env.scenario.charger_xy})
    for i in range(env.max_steps):
        _, _, terminated, truncated, _ = env.step(np.zeros(2, dtype=np.float32))
        assert not terminated
        assert truncated == (i == env.max_steps - 1)
    assert env.max_steps == 1200


def test_rewards_sum_to_drive_reduction():
    env = HomeostaticArena("foraging", seed=3)
    _, info0 = env.reset()
    rng = np.random.default_rng(0)
    total = 0.0
    for _ in range(300):
        _, r, terminated, truncated, info = env.step(rng.uniform(-1, 1, 2).astype(np.float32))
        total += r
        assert not terminated
    assert total == pytest.approx(info0["drive"] - homeostatic_drive(info["energy"],
                                                                     info["damage"]))


def test_random_starts_are_valid_and_vary():
    env = HomeostaticArena("foraging")
    starts = set()
    for seed in range(50):
        _, info = env.reset(seed=seed)
        xy = (info["x"], info["y"])
        assert ambient_temperature(xy, env.scenario.heat_sources) < 30.0
        assert math.dist(xy, env.scenario.charger_xy) >= 2.0
        assert max(abs(c) for c in xy) <= env.scenario.half_size - 0.5
        assert info["skin_c"] < 30.0 and info["skin_c"] >= AMBIENT_C
        starts.add(xy)
    assert len(starts) == 50


def test_same_seed_same_trajectory():
    def trajectory(seed):
        env = HomeostaticArena(foraging(), seed=seed)
        obs, _ = env.reset()
        rng = np.random.default_rng(123)
        out = [obs]
        for _ in range(300):
            obs, *_ = env.step(rng.uniform(-1, 1, 2).astype(np.float32))
            out.append(obs)
        return np.array(out)

    a, b, c = trajectory(42), trajectory(42), trajectory(43)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
