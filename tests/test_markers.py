"""Tests for the marker statistics, episode segmentation and trade-off design."""
import math

import numpy as np
import pytest

from agents import make_agent
from experiments.markers import (
    TRADEOFF_START_ENERGIES,
    EpisodeLog,
    bootstrap_diff,
    bootstrap_mean,
    crossed_through_wall,
    detour_path,
    find_encounters,
    fit_logistic,
    foraging_episode_metrics,
    survival_marker,
    anticipation_marker,
    sensitization_marker,
    tradeoff_design_check,
    tradeoff_marker,
    wilson,
)
from arena.physiology import PhysiologyParams, ambient_temperature
from arena.scenarios import tradeoff


# ------------------------------------------------------------------ statistics
def test_wilson_interval():
    m = wilson(15, 30)
    assert m.mean == 0.5 and m.n == 30
    assert m.ci_low == pytest.approx(0.332, abs=0.002)
    assert m.ci_high == pytest.approx(0.668, abs=0.002)
    zero = wilson(0, 30)
    assert zero.mean == 0.0 and zero.ci_low == 0.0 and 0.10 < zero.ci_high < 0.13
    assert math.isnan(wilson(0, 0).mean)


def test_bootstrap_mean_and_diff():
    m = bootstrap_mean([2.0] * 10)
    assert m.mean == m.ci_low == m.ci_high == 2.0
    m = bootstrap_mean([0.0, 1.0] * 50 + [math.nan])
    assert m.n == 100 and m.ci_low < 0.5 < m.ci_high
    d = bootstrap_diff([1.0] * 30, [0.0] * 30)
    assert d.mean == d.ci_low == d.ci_high == 1.0 and d.n == 60


def test_logistic_recovers_slope():
    rng = np.random.default_rng(0)
    x = rng.uniform(0, 1, 5000)
    y = rng.random(5000) < 1 / (1 + np.exp(-(1.0 - 3.0 * x)))
    intercept, slope = fit_logistic(x, y)
    assert intercept == pytest.approx(1.0, abs=0.2)
    assert slope == pytest.approx(-3.0, abs=0.3)
    assert all(math.isnan(v) for v in fit_logistic(x, np.zeros_like(x)))
    # Perfect separation stays finite thanks to the ridge penalty.
    assert np.isfinite(fit_logistic([0.1] * 10 + [0.9] * 10, [1] * 10 + [0] * 10)[1])


# ------------------------------------------------------------------ encounters
def test_find_encounters_hysteresis_and_harm():
    amb = np.array([25, 39, 45, 36, 34, 25, 40, 50, 37, 30, 41, 42], dtype=float)
    noc = np.array([0, 0, .2, .1, 0, 0, 0, .9, .6, 0, 0, .1])
    enc = find_encounters(amb, noc)
    assert [(e.start, e.end) for e in enc] == [(1, 4), (6, 9), (10, 12)]
    assert [e.peak_ambient_c for e in enc] == [45, 50, 42]
    assert [e.harmful for e in enc] == [False, True, False]


def _log(amb, noc, died=False):
    n = len(amb)
    data = {"t": np.arange(n) * 0.05, "x": np.zeros(n), "y": np.zeros(n),
            "ambient_c": np.asarray(amb, float), "skin_c": np.zeros(n),
            "nociceptor": np.asarray(noc, float), "energy": np.ones(n),
            "damage": np.zeros(n), "damage_taken": np.zeros(n),
            "on_charger": np.zeros(n, bool), "touch": np.zeros(n), "drive": np.zeros(n)}
    return EpisodeLog("test", "foraging", 0, 1.0, 0.05, died, data)


def test_foraging_episode_metrics_sensitization():
    #          enc0 (40, safe)  enc1 (44, safe)  enc2 (55, HARM)  enc3 (39 safe)  enc4 (52 HARM)
    amb = [25, 40, 30, 25, 44, 30, 25, 55, 30, 25, 39, 30, 25, 52, 30]
    noc = [0, .0, 0, 0, .1, 0, 0, .9, 0, 0, .0, 0, 0, .8, 0]
    m = foraging_episode_metrics(_log(amb, noc))
    assert m["n_encounters"] == 5 and m["n_harmful"] == 2
    assert m["anticipation_rate"] == pytest.approx(3 / 5)
    assert m["sens_n_before"] == 2 and m["sens_n_after"] == 2
    assert m["sensitization_c"] == pytest.approx((39 + 52) / 2 - (40 + 44) / 2)
    assert m["sensitization_nonharmful_c"] == pytest.approx(39 - (40 + 44) / 2)
    empty = foraging_episode_metrics(_log([25] * 10, [0] * 10))
    assert empty["n_encounters"] == 0 and math.isnan(empty["anticipation_rate"])
    assert math.isnan(empty["sensitization_c"])


# ------------------------------------------------------------------ trade-off
def test_crossing_detection():
    x = np.linspace(-3, 3, 100)
    assert crossed_through_wall(x, np.zeros(100), 3.3)                   # straight through
    assert not crossed_through_wall(x, np.full(100, 4.2), 3.3)           # around the end
    back = np.concatenate([np.linspace(-3, -0.1, 50), np.linspace(-0.1, -3, 50)])
    assert not crossed_through_wall(back, np.zeros(100), 3.3)            # entered, withdrew
    y = np.where(np.abs(x) < 0.3, 3.6, 0.0)                              # skirted the tip
    assert not crossed_through_wall(x, y, 3.3)
    assert not crossed_through_wall(x[::-1], np.zeros(100), 3.3)         # east to west


def test_detour_path_is_damage_free_and_ends_at_charger():
    s = tradeoff(0.9)
    params = PhysiologyParams()
    path = detour_path(s, params)
    assert tuple(path[0]) == s.start_xy and tuple(path[-1]) == s.charger_xy
    assert max(ambient_temperature(p, s.heat_sources) for p in path) <= 45.0 + 1e-6
    assert max(abs(p[1]) for p in path) < s.half_size - 0.25   # stays inside the arena


def test_tradeoff_design_holds():
    check = tradeoff_design_check(TRADEOFF_START_ENERGIES)
    failed = [k for k, ok in check["conditions"].items() if not ok]
    assert failed == []


# ------------------------------------------------------------------ smoke tests
def test_markers_run_end_to_end_small():
    factory = lambda seed: make_agent("reflex_thermotactic", seed)  # noqa: E731
    surv = survival_marker(factory, n_seeds=2, agent_name="reflex_thermotactic")
    assert set(surv.metrics) >= {"survived_frac", "survival_time_s", "time_on_charger_s"}
    assert len(surv.logs) == 2 and len(surv.episodes) == 2
    ant = anticipation_marker(logs=surv.logs)
    assert "anticipation_rate" in ant.metrics
    sens = sensitization_marker(logs=surv.logs)
    assert "sensitization_c" in sens.metrics
    trade = tradeoff_marker(factory, n_seeds=2, start_energies=(0.08, 0.9),
                            agent_name="reflex_thermotactic")
    assert len(trade.episodes) == 4
    assert {"tradeoff_score", "logistic_slope", "crossing_rate@0.08"} <= set(trade.metrics)
