"""Tests for the pre-registered pass rules applied by experiments/run_v02.py."""
from experiments.markers import Metric
from experiments.run_v02 import HYPOTHESES, verdicts

POS = Metric(0.5, 0.2, 0.8, 80)      # CI excludes 0, predicted direction
NULL = Metric(0.0, -0.3, 0.3, 80)    # CI includes 0


def run(variant, seed, effect, gate_ok=True, applicable=True):
    effects = {h: effect for h in HYPOTHESES}
    effects["H3b_applicable_spont_minus_other"] = POS if applicable else NULL
    effects["S1_other_minus_self"] = NULL
    res = {"spec": {"label": f"{variant}_seed{seed}", "variant": variant, "seed": seed},
           "effects": effects, "attribution": {"position:SELF": 1.0}}
    if variant in ("FULL", "NOEFF", "NOFWD"):
        res["gate"] = {"fwd_mse": 0.5 if gate_ok else 0.9, "nochange_mse": 1.0}
    return res


def controls(untrained_effect=NULL):
    out = [run("UNTRAINED", s, untrained_effect) for s in range(5)]
    comp = run("COMPARATOR", None, POS)
    nochange = run("NO-CHANGE", None, NULL)
    nochange["attribution"] = {"position:SELF": 1.0, "position:OTHER-ONPAD": 0.0}
    return out + [comp, nochange]


def test_four_of_five_passing_runs_support_a_hypothesis():
    results = [run("FULL", s, POS) for s in range(4)] + [run("FULL", 4, NULL)] + controls()
    v = verdicts(results)
    assert v["FULL:H1_spont_minus_self"]["verdict"] == "supported"
    assert v["FULL:H1_spont_minus_self"]["passing_runs"] == 4
    assert v["V1_untrained_not_fooled"]["ok"] and v["V2_comparator_passes_H1_H2"]["ok"]
    assert v["V3_position_rule_accuracy"]["position:OTHER-ONPAD"] == 0.0


def test_gate_failures_count_as_not_supporting():
    results = [run("FULL", s, POS, gate_ok=s < 3) for s in range(5)] + controls()
    assert verdicts(results)["FULL:H1_spont_minus_self"]["verdict"] == "not supported"


def test_missing_runs_count_as_not_supporting():
    results = [run("FULL", s, POS) for s in range(3)] + controls()
    results.append({"spec": {"label": "FULL_seed3", "variant": "FULL", "seed": 3},
                    "missing": True})
    assert verdicts(results)["FULL:H1_spont_minus_self"]["verdict"] == "not supported"


def test_h3b_not_applicable_when_agent_does_not_predict_other():
    results = [run("FULL", s, POS, applicable=False) for s in range(5)] + controls()
    v = verdicts(results)["FULL:H3b_otherblind_interaction"]
    assert v["verdict"] == "not applicable" and v["not_applicable"] == 5


def test_untrained_passing_flags_a_fooled_test():
    results = [run("FULL", s, POS) for s in range(5)] + controls(untrained_effect=POS)
    v = verdicts(results)
    assert not v["V1_untrained_not_fooled"]["ok"]
    assert "H1_spont_minus_self" in v["V1_untrained_not_fooled"]["fooled_by_untrained"]
