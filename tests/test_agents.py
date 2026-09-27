"""Tests for the random and reflex agents."""
import math

import numpy as np
import pytest

from agents import AGENT_NAMES, MINIMAL_CONTROL_NAMES, ReflexAgent, make_agent
from arena.env import OBS_NAMES, HomeostaticArena

I = {name: i for i, name in enumerate(OBS_NAMES)}


def synthetic_obs(nociceptor=0.0, ambient_c=25.0, beacon=0.2, touch=0.0, energy=1.0):
    obs = np.zeros(len(OBS_NAMES), dtype=np.float32)
    obs[I["ambient_temp"]] = (ambient_c - 25.0) / 35.0
    obs[I["nociceptor"]] = nociceptor
    obs[I["beacon"]] = beacon
    obs[I["touch"]] = touch
    obs[I["energy"]] = energy
    return obs


@pytest.mark.parametrize("name", AGENT_NAMES)
def test_valid_actions_for_200_steps(name):
    env = HomeostaticArena("foraging", seed=0)
    agent = make_agent(name, seed=0)
    obs, info = env.reset()
    agent.reset()
    for _ in range(200):
        action = agent.act(obs, info)
        assert action.shape == (2,) and action.dtype == np.float32
        assert np.all(np.isfinite(action)) and np.all(np.abs(action) <= 1.0)
        obs, _, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            obs, info = env.reset()
            agent.reset()


def test_unknown_agent_and_mode_rejected():
    with pytest.raises(ValueError):
        make_agent("oracle")
    with pytest.raises(ValueError):
        ReflexAgent("clairvoyant")


def test_agents_do_not_need_info():
    for name in AGENT_NAMES:
        make_agent(name, seed=0).act(synthetic_obs(), None)


def test_same_seed_same_actions_after_reset():
    agent = make_agent("reflex_thermotactic", seed=5)
    a = [agent.act(synthetic_obs(energy=0.3, beacon=0.2 - 0.001 * i)) for i in range(50)]
    agent.reset()
    b = [agent.act(synthetic_obs(energy=0.3, beacon=0.2 - 0.001 * i)) for i in range(50)]
    assert np.array_equal(np.array(a), np.array(b))


@pytest.mark.parametrize("mode", ["nociceptive", "thermotactic"])
def test_reverses_heading_within_one_step_of_nociceptor(mode):
    agent = ReflexAgent(mode, seed=0, wander_noise=0.0)
    before = agent.act(synthetic_obs(nociceptor=0.0))
    after = agent.act(synthetic_obs(nociceptor=0.5))
    assert agent.last_rule == "withdraw"
    cos = float(before @ after) / (np.linalg.norm(before) * np.linalg.norm(after))
    assert cos < -0.8
    # Heading is held for the refractory period even if the input changes.
    held = [agent.act(synthetic_obs(nociceptor=0.0, touch=1.0))
            for _ in range(ReflexAgent.REFRACTORY_STEPS)]
    assert all(np.allclose(h, after) for h in held)
    assert agent.act(synthetic_obs(touch=1.0)) is not None and agent.last_rule == "wall"


def _run_refractory(agent, obs):
    for _ in range(ReflexAgent.REFRACTORY_STEPS):
        agent.act(obs)
        assert agent.last_rule == "refractory"


def test_sustained_withdrawal_keeps_escaping_while_stimulus_persists():
    agent = ReflexAgent("nociceptive", seed=0)            # default: sustained
    hot = synthetic_obs(nociceptor=0.9)
    first = agent.act(hot)
    assert agent.last_rule == "withdraw"
    _run_refractory(agent, hot)
    again = agent.act(hot)                                 # still hot after refractory
    assert agent.last_rule == "escape" and np.allclose(again, first)
    agent.act(synthetic_obs(nociceptor=0.0))               # stimulus gone
    assert agent.last_rule == "wander" and not agent.escaping


def test_sustained_withdrawal_reverses_again_if_heat_keeps_rising():
    agent = ReflexAgent("nociceptive", seed=0)
    agent.act(synthetic_obs(nociceptor=0.9, ambient_c=50.0))
    _run_refractory(agent, synthetic_obs(nociceptor=0.9, ambient_c=52.0))
    moving = synthetic_obs(nociceptor=0.9, ambient_c=54.0)   # still getting hotter
    moving[I["vel_x"]] = 0.5
    action = agent.act(moving)
    assert agent.last_rule == "withdraw" and action[0] < 0     # away from the motion


def test_literal_withdrawal_flips_back_when_stimulus_persists():
    agent = ReflexAgent("nociceptive", seed=0, withdrawal="literal")
    hot = synthetic_obs(nociceptor=0.9)
    first = agent.act(hot)
    _run_refractory(agent, hot)
    again = agent.act(hot)
    assert agent.last_rule == "withdraw"
    assert float(first @ again) < 0                        # reversed back again


def test_sustained_withdrawal_reverses_actual_motion_not_heading():
    # Heading points east, but the body is still moving west (velocity lags heading,
    # e.g. right after a tumble). Withdrawal must send it east (away from the motion).
    for style, expected_x_sign in [("sustained", +1), ("literal", -1)]:
        agent = ReflexAgent("nociceptive", seed=0, withdrawal=style)
        agent.heading = 0.0
        obs = synthetic_obs(nociceptor=0.9)
        obs[I["vel_x"]] = -0.6
        action = agent.act(obs)
        assert np.sign(action[0]) == expected_x_sign, style


def test_thermal_trigger_logic():
    noci = ReflexAgent("nociceptive", seed=0)
    thermo = ReflexAgent("thermotactic", seed=0)
    for agent in (noci, thermo):
        agent.prev_ambient_c = 36.0
    assert thermo.withdrawal_triggered(0.0, 36.5)         # hot and rising
    assert not thermo.withdrawal_triggered(0.0, 35.5)     # hot but falling
    thermo.prev_ambient_c = 33.0
    assert not thermo.withdrawal_triggered(0.0, 34.0)     # rising but below 35 C
    assert not noci.withdrawal_triggered(0.0, 50.0)       # nociceptive ignores ambient
    assert noci.withdrawal_triggered(0.2, 30.0)


@pytest.mark.parametrize("name", MINIMAL_CONTROL_NAMES)
def test_minimal_controls_run_in_the_arena(name):
    env = HomeostaticArena("tradeoff", seed=0)
    agent = make_agent(name, seed=0)
    obs, info = env.reset()
    for _ in range(100):
        action = agent.act(obs, info)
        assert action.shape == (2,) and np.all(np.abs(action) <= 1.0)
        obs, _, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break


def test_motivational_reflex_ignores_heat_only_when_energy_is_critical():
    agent = make_agent("reflex_motivational", seed=0)
    agent.act(synthetic_obs(ambient_c=36.0, energy=0.5))
    agent._energy = 0.5
    assert agent.withdrawal_triggered(0.0, 37.0)          # thermotactic rule as usual
    assert agent.withdrawal_triggered(0.9, 50.0)
    agent._energy = 0.1
    assert not agent.withdrawal_triggered(0.0, 37.0)      # critical need vetoes withdrawal
    assert not agent.withdrawal_triggered(0.9, 50.0)


def test_sensitizing_reflex_lowers_threshold_after_harm_only():
    agent = make_agent("reflex_sensitizing", seed=0)
    agent.prev_ambient_c = 36.0
    assert not agent.withdrawal_triggered(0.0, 37.0)      # naive: nociceptive rule only
    assert agent.withdrawal_triggered(0.6, 50.0)          # harmful stimulus sets the latch
    agent.prev_ambient_c = 36.0
    assert agent.withdrawal_triggered(0.0, 37.0)          # now withdraws on rising heat
    agent.prev_ambient_c = 37.0
    assert not agent.withdrawal_triggered(0.0, 36.5)      # ... but not on falling heat
    agent.reset()
    assert not agent.sensitized


def test_tumbles_only_when_foraging_and_beacon_falls():
    agent = ReflexAgent("nociceptive", seed=0)
    agent.act(synthetic_obs(energy=0.3, beacon=0.30))
    rules = set()
    for _ in range(40):
        agent.prev_beacon = 0.30
        agent.act(synthetic_obs(energy=0.3, beacon=0.29))
        rules.add(agent.last_rule)
    assert rules == {"tumble", "run"}
    agent.prev_beacon = 0.30
    agent.act(synthetic_obs(energy=0.3, beacon=0.31))
    assert agent.last_rule == "run"
    agent.act(synthetic_obs(energy=0.9, beacon=0.1))
    assert agent.last_rule == "wander"


def approach_heat(mode: str):
    """Walk straight north toward a 60 C hot spot from 3 m away (no sensor noise).

    Returns (nociceptor at first withdrawal, max nociceptor over the run,
    step of first withdrawal, list of nociceptor values seen by the agent).
    """
    env = HomeostaticArena("foraging", sensor_noise=False)
    source = env.scenario.heat_sources[0].p0            # (-1.5, 1.5)
    start = (source[0], source[1] - 3.0)
    obs, info = env.reset(seed=0, options={"start_xy": start})
    agent = ReflexAgent(mode, seed=0, wander_noise=0.0)
    agent.heading = math.pi / 2
    noci_seen, first = [], None
    for step in range(int(4.0 / env.dt)):
        noci_seen.append(float(obs[I["nociceptor"]]))
        action = agent.act(obs, None)
        if agent.last_rule == "withdraw" and first is None:
            first = (noci_seen[-1], step)
        obs, _, terminated, _, info = env.step(action)
        if terminated:
            break
    return first[0], max(noci_seen), first[1], noci_seen


def test_thermotactic_turns_away_before_nociceptor_fires():
    noci_at_turn, noci_max, step, _ = approach_heat("thermotactic")
    assert noci_at_turn <= 0.1
    assert noci_max < 0.1       # never heated enough to trigger the nociceptive rule


def test_nociceptive_reflex_waits_for_nociceptor_and_reacts_within_one_step():
    noci_at_turn, noci_max, step, seen = approach_heat("nociceptive")
    first_above = next(i for i, n in enumerate(seen) if n > 0.1)
    assert step == first_above          # withdrew on the very first supra-threshold input
    assert noci_at_turn > 0.1 and noci_max > 0.1
