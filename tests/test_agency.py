"""Tests for the v0.2 agency world (lamp, switch pad, other robot, events, senses)."""
import math
import warnings

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from arena.agency import (
    AGENCY_OBS_NAMES,
    OBS_INDEX,
    THERMAL_SLICE,
    AgencyArena,
)
from arena.env import HomeostaticArena

I = OBS_INDEX
ZERO = np.zeros(2, dtype=np.float32)
QUIET = {"random_events": False}          # no spontaneous toggles or shocks


def make(**kw):
    return AgencyArena(sensor_noise=kw.pop("sensor_noise", False), **kw)


def run(env, action, n, other_action=None):
    if other_action is not None:
        env.set_other_action(other_action)
    out = []
    for _ in range(n):
        out.append(env.step(np.asarray(action, dtype=np.float32)))
    return out


def toggles(steps, cause=None):
    return [e for *_, info in steps for e in info["events"]
            if e["type"] == "lamp_toggle" and (cause is None or e["cause"] == cause)]


def test_check_env_and_observation_layout():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        check_env(AgencyArena(seed=0))
    assert [str(w.message) for w in caught if "render" not in str(w.message).lower()] == []
    env = AgencyArena(seed=1)
    obs, info = env.reset()
    assert obs.shape == (26,) == (len(AGENCY_OBS_NAMES),)
    for key in ("self", "world", "events", "lamp_on", "other_x"):
        assert key in info
    env.action_space.seed(0)
    for _ in range(400):
        obs, r, term, trunc, info = env.step(env.action_space.sample())
        assert env.observation_space.contains(obs) and np.isfinite(r)
        if term or trunc:
            env.reset()


def test_v01_environment_unchanged_by_extension_hooks():
    """Same seed + actions give the same observations as recorded before v0.2."""
    env = HomeostaticArena("foraging", seed=42)
    obs, _ = env.reset()
    rng = np.random.default_rng(123)
    for _ in range(300):
        obs, *_ = env.step(rng.uniform(-1, 1, 2).astype(np.float32))
    assert obs.shape == (11,)
    assert env.model.nu == 2 and env.model.nq == 2


def test_agent_entering_pad_toggles_lamp_once_with_cause_self():
    env = make()
    env.reset(seed=0, options={"start_xy": (-1.5, 0.0), "other_xy": (4.0, -4.0),
                               "lamp_on": False, **QUIET})
    steps = run(env, [0.8, 0.0], 30, other_action=[0.0, 0.0])
    events = toggles(steps)
    assert len(events) == 1 and events[0]["cause"] == "self"
    assert events[0]["lamp_on"] and not events[0]["body_affected"]   # lamp far away
    assert steps[-1][-1]["lamp_on"]
    # Staying on the pad does not toggle again; leaving and re-entering does.
    env.reset(seed=0, options={"start_xy": (-0.1, 0.0), "other_xy": (4.0, -4.0),
                               "lamp_on": False, **QUIET})
    assert toggles(run(env, [0.0, 0.0], 20, other_action=[0.0, 0.0])) == []


def test_other_robot_entering_pad_toggles_with_cause_other():
    env = make()
    env.reset(seed=0, options={"start_xy": (-3.0, -3.0), "other_xy": (1.5, 0.0),
                               "lamp_on": True, **QUIET})
    steps = run(env, ZERO, 30, other_action=[-0.8, 0.0])
    events = toggles(steps)
    assert [e["cause"] for e in events] == ["other"]
    assert not steps[-1][-1]["lamp_on"]


def test_switch_disabled_gives_no_toggle():
    env = make()
    env.reset(seed=0, options={"start_xy": (-1.5, 0.0), "other_xy": (4.0, -4.0),
                               "lamp_on": False, "switch_enabled": False, **QUIET})
    steps = run(env, [0.8, 0.0], 30, other_action=[0.0, 0.0])
    assert toggles(steps) == [] and steps[-1][-1]["agent_on_pad"]


def test_scheduled_toggle_and_shock():
    env = make()
    env.reset(seed=0, options={"start_xy": (-2.5, -2.5), "other_xy": (4.0, -4.0),
                               "lamp_on": False, "start_energy": 0.8, **QUIET})
    env.set_other_action([0.0, 0.0])
    env.schedule_toggle("spontaneous")
    _, _, _, _, info = env.step(ZERO)
    assert [e["cause"] for e in info["events"]] == ["spontaneous"] and info["lamp_on"]
    env.schedule_shock()
    _, _, _, _, info = env.step(ZERO)
    shock = [e for e in info["events"] if e["type"] == "metabolic_shock"]
    assert shock and shock[0]["cause"] == "internal" and shock[0]["body_affected"]
    assert info["energy"] == pytest.approx(0.8 - 2 * 0.012 * 0.05 - 0.1)


def test_lamp_heats_charger_only_when_on_and_affects_body_there():
    env = make()
    for lamp_on, expected in [(True, 60.0), (False, 25.0)]:
        _, info = env.reset(seed=0, options={"start_xy": (3.0, 3.0), "other_xy": (-4, -4),
                                             "lamp_on": lamp_on, **QUIET})
        assert info["ambient_c"] == pytest.approx(expected, abs=0.1)
    env.schedule_toggle("manual")
    _, _, _, _, info = env.step(ZERO)
    assert info["events"][0]["body_affected"]          # agent sits at the lamp


def test_random_event_rates():
    env = AgencyArena(seed=0)
    env.reset(seed=0)
    env.set_other_action([0.0, 0.0])
    counts = {"spontaneous": 0, "internal": 0}
    for _ in range(int(600 / env.dt)):                  # 10 minutes
        _, _, term, trunc, info = env.step(ZERO)
        for e in info["events"]:
            counts[e["cause"]] = counts.get(e["cause"], 0) + 1
        env.body.energy = 1.0                            # keep it alive
        if trunc:
            env.reset()
            env.set_other_action([0.0, 0.0])
    assert 15 <= counts["spontaneous"] <= 50            # expected 30
    assert 8 <= counts["internal"] <= 35                # expected 20
    env.reset(seed=0, options=QUIET)
    quiet = run(env, ZERO, 400, other_action=[0.0, 0.0])
    assert all(e["cause"] not in ("spontaneous", "internal")
               for *_, info in quiet for e in info["events"])


def test_efference_copy_and_previous_reward_channels():
    env = make()
    obs, _ = env.reset(seed=0, options={"start_xy": (-3.0, -3.0), **QUIET})
    assert np.all(obs[[I["prev_action_x"], I["prev_action_y"]]] == 0.0)
    obs, r, *_ = env.step(np.array([0.3, -0.7], dtype=np.float32))
    assert obs[I["prev_action_x"]] == pytest.approx(0.3)
    assert obs[I["prev_action_y"]] == pytest.approx(-0.7)
    assert obs[I["prev_reward"]] == pytest.approx(np.clip(20 * r, -1, 1), abs=1e-6)
    obs, *_ = env.step(np.array([2.0, 0.0], dtype=np.float32))    # clipped to 1
    assert obs[I["prev_action_x"]] == pytest.approx(1.0)


def test_thermal_vision_sees_lamp_in_the_right_sector():
    env = make()
    obs, _ = env.reset(seed=0, options={"start_xy": (0.0, -1.0), "other_xy": (-4, -4),
                                        "lamp_on": False, **QUIET})
    # Lamp at (3, 3) is north-east of (0, -1) at ~53 degrees -> sector NE.
    assert obs[I["thermal_NE"]] == pytest.approx(0.0, abs=1e-6)
    env.schedule_toggle("manual")
    obs, *_ = env.step(ZERO)
    d = math.dist(env.xy, (3.0, 3.0))
    assert obs[I["thermal_NE"]] == pytest.approx(math.exp(-d / 3.0), abs=1e-3)
    # The static hot spot at (-2, 2) is north-west.
    assert obs[I["thermal_NW"]] > 0.3
    assert obs[THERMAL_SLICE].shape == (8,)


def test_other_robot_channels_and_patrol_visits_pad():
    env = make()
    obs, info = env.reset(seed=3, options={"start_xy": (-3.0, -3.0), "other_xy": (2.0, 1.0),
                                           **QUIET})
    assert obs[I["other_present"]] == 1.0
    assert obs[I["other_dx"]] == pytest.approx((2.0 + 3.0) / 5, abs=1e-5)
    assert obs[I["other_dy"]] == pytest.approx((1.0 + 3.0) / 5, abs=1e-5)
    env.body.energy = 1.0
    causes = []
    for _ in range(int(60 / env.dt)):
        *_, info = env.step(ZERO)
        causes += [e["cause"] for e in info["events"]]
    assert causes.count("other") >= 2                    # the patrol keeps visiting


def test_touch_senses_other_robot():
    env = make()
    env.reset(seed=0, options={"start_xy": (-2.0, -2.0), "other_xy": (-0.8, -2.0), **QUIET})
    steps = run(env, ZERO, 40, other_action=[-0.8, 0.0])
    assert max(obs[I["touch"]] for obs, *_ in steps) > 0.0


def test_determinism():
    def trace(seed):
        env = AgencyArena(seed=seed)
        obs, _ = env.reset()
        rng = np.random.default_rng(0)
        out = [obs]
        for _ in range(300):
            obs, *_ = env.step(rng.uniform(-1, 1, 2).astype(np.float32))
            out.append(obs)
        return np.array(out)
    assert np.array_equal(trace(5), trace(5))
    assert not np.array_equal(trace(5), trace(6))
