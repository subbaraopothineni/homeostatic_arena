"""Tests for the v0.2 evaluation pipeline, using controls with known answers."""
import math

import numpy as np
import pytest

from experiments.agency_tests import (
    ComparatorPredictor,
    NetworkPredictor,
    NoChangePredictor,
    attribution_accuracy,
    hypothesis_effects,
    passes,
    probe_accuracy,
    run_t1_trial,
    run_t2,
    self_event_step,
)
from experiments.train_agent import make_net

N = 6   # trials per condition (the real run uses 40)


@pytest.fixture(scope="module")
def spont_step():
    return self_event_step(n=6)


@pytest.fixture(scope="module")
def comparator_trials(spont_step):
    return run_t2(ComparatorPredictor, spont_step, trials=N)


def test_every_trial_has_its_event_with_the_right_cause(comparator_trials):
    expected = {"SELF": {"self"}, "OTHER": {"other"}, "SPONT": {"spontaneous"},
                "NOEVENT": set(), "SELF-OMIT": set(), "OTHER-ONPAD": {"other"},
                "SPONT-ONPAD": {"spontaneous"}}
    for t in comparator_trials:
        assert t.event_step is not None, (t.condition, t.ablation, t.index)
        assert set(t.causes) == expected[t.condition]


def test_no_change_predictor_passes_nothing(spont_step):
    trials = run_t2(NoChangePredictor, spont_step, trials=N)
    for name, m in hypothesis_effects(trials).items():
        assert not passes(m), name
    rel = [t.rel_pe for t in trials if t.condition in ("SELF", "OTHER", "SPONT")]
    assert np.allclose(rel, 1.0)


def test_comparator_positive_control_passes_h1_h2_h3a(comparator_trials):
    effects = hypothesis_effects(comparator_trials)
    assert passes(effects["H1_spont_minus_self"])
    assert passes(effects["H2_omit_minus_noevent"])
    assert passes(effects["H3a_selfblind_interaction"])
    assert not passes(effects["H3b_applicable_spont_minus_other"])   # it cannot predict others


def test_position_rule_fails_dissociation_trials(comparator_trials):
    acc = attribution_accuracy(comparator_trials)
    assert acc["position:SELF"] == 1.0
    assert acc["position:OTHER-ONPAD"] == 0.0 and acc["position:SPONT-ONPAD"] == 0.0
    assert acc["pe:SELF"] == 1.0 and acc["pe:OTHER-ONPAD"] == 1.0


def test_network_predictor_runs_and_records_memory(spont_step):
    net = make_net("UNTRAINED", 0)
    trials = run_t2(lambda: NetworkPredictor(net, "UNTRAINED"), spont_step, trials=2)
    assert all(t.event_step is not None for t in trials)
    t = trials[0]
    assert set(t.states) == {1, 10, 40} and t.states[1].shape == (128,)
    assert t.raw_windows[1].shape == (5 * 26,)


def test_t1_no_change_separates_body_from_world_trivially():
    world = run_t1_trial(NoChangePredictor(), "WORLD", True, 0)
    body = run_t1_trial(NoChangePredictor(), "BODY", True, 0)
    assert world["intero_share"] < 0.1 and not world["body_affected"]
    assert body["intero_share"] > 0.9 and body["body_affected"]


def test_probe_accuracy_on_synthetic_data():
    rng = np.random.default_rng(0)
    labels = np.array(["a", "b", "c"] * 30)
    separable = rng.normal(size=(90, 10))
    separable[:, 0] += np.array([{"a": 0, "b": 5, "c": 10}[c] for c in labels])
    assert probe_accuracy(separable, labels) > 0.95
    noise = rng.normal(size=(90, 10))
    assert probe_accuracy(noise, labels) < 0.6
