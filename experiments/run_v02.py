"""Run the pre-registered v0.2 tests and write CSVs, figures and a report.

Usage (from the repository root, after experiments/train_all.sh):
    python -m experiments.run_v02 --models results/v02/models --out results/v02

Pass rules are applied exactly as registered in docs/preregistration_v0.2.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import torch

from agents.recurrent import RecurrentAgent, load_model
from agents.reflex import ReflexAgent
from experiments.agency_tests import (
    T1_CONDITIONS,
    TRIALS_PER_CONDITION,
    ComparatorPredictor,
    NetworkPredictor,
    NoChangePredictor,
    attribution_accuracy,
    free_running,
    hypothesis_effects,
    passes,
    probe_accuracy,
    relpe_by_condition,
    run_t1_behaviour,
    run_t1_trial,
    run_t2,
    self_event_step,
)
from experiments.markers import Metric, bootstrap_mean

REGISTERED = {"FULL": range(5), "NOEFF": range(3), "NOFWD": range(3), "UNTRAINED": range(5)}
TRAINED = ("FULL", "NOEFF", "NOFWD")
HYPOTHESES = ("H1_spont_minus_self", "H2_omit_minus_noevent", "H3a_selfblind_interaction",
              "H3b_otherblind_interaction")
GATE_RATIO = 0.8
SUPPORT_MIN = 4
GATE_EPISODES, ECOLOGICAL_EPISODES = 20, 50


def predictor_specs(models: Path) -> list[dict]:
    specs = []
    for variant, seeds in REGISTERED.items():
        for s in seeds:
            path = models / f"{variant}_seed{s}.pt"
            specs.append({"label": f"{variant}_seed{s}", "variant": variant, "seed": s,
                          "path": str(path) if path.exists() else None})
    specs += [{"label": n, "variant": n, "seed": None, "path": None}
              for n in ("COMPARATOR", "NO-CHANGE")]
    return specs


def _probes(t2, t1_rows, raw: bool) -> dict[str, float]:
    """Exploratory: decode who caused a lamp change, and what happened (T1)."""
    out = {}
    base = [t for t in t2 if t.ablation == "none" and t.condition in ("SELF", "OTHER", "SPONT")]
    labels = np.array([t.condition for t in base])
    for lag in (1, 10, 40):
        X = np.stack([(t.raw_windows if raw else t.states)[lag] for t in base])
        out[f"who@{lag}"] = probe_accuracy(X, labels)
    labels = np.array([r["condition"] for r in t1_rows])
    for lag in (1, 9):
        X = np.stack([(r["raw_windows"] if raw else r["states"])[lag] for r in t1_rows])
        out[f"what@{lag}"] = probe_accuracy(X, labels)
    return out


def evaluate(job) -> dict:
    """Every test for one predictor (runs in a worker process)."""
    spec, spont_step, trials, world = job
    torch.set_num_threads(1)
    t0 = time.perf_counter()
    res = {"spec": spec}
    if spec["variant"] == "REFLEX":
        agent = ReflexAgent("thermotactic", seed=0)
        res["t1_behaviour"] = [run_t1_behaviour(agent, c, i) for c in T1_CONDITIONS
                               for i in range(trials)]
        res["seconds"] = time.perf_counter() - t0
        return res
    net = None
    if spec["variant"] == "COMPARATOR":
        factory = ComparatorPredictor
    elif spec["variant"] == "NO-CHANGE":
        factory = NoChangePredictor
    elif spec["path"] is None:
        res["missing"] = True
        return res
    else:
        net, _ = load_model(spec["path"])
        factory = lambda: NetworkPredictor(net, spec["label"])  # noqa: E731

    t2 = run_t2(factory, spont_step, trials)
    t1 = [run_t1_trial(factory(), c, i % 2 == 0, i) for c in T1_CONDITIONS for i in range(trials)]
    res["effects"] = hypothesis_effects(t2)
    res["relpe"] = relpe_by_condition(t2)
    res["attribution"] = attribution_accuracy(t2)
    res["t2_rows"] = [{"condition": t.condition, "ablation": t.ablation, "lamp_on": t.lamp_on,
                       "index": t.index, "event_step": t.event_step, "rel_pe": t.rel_pe,
                       "abs_pe": t.abs_pe, "causes": "+".join(t.causes),
                       "agent_on_pad_after": t.agent_on_pad_after} for t in t2]
    res["t1_rows"] = [{k: v for k, v in r.items() if k not in ("states", "raw_windows")}
                      for r in t1]
    if net is not None:
        res["probes"] = _probes(t2, t1, raw=False)
    if spec["variant"] == "NO-CHANGE":                     # raw-input probe baseline
        res["probes"] = _probes(t2, t1, raw=True)
    if spec["variant"] in TRAINED:
        gate = free_running(net, GATE_EPISODES, seed0=900_000, world=world)
        gate.pop("natural")
        res["gate"] = gate
    if spec["variant"] == "FULL":
        res["ecological"] = free_running(net, ECOLOGICAL_EPISODES, seed0=800_000,
                                         world=world)["natural"]
        res["t1_behaviour"] = [run_t1_behaviour(RecurrentAgent(net), c, i)
                               for c in T1_CONDITIONS for i in range(trials)]
    res["seconds"] = time.perf_counter() - t0
    return res


# ==========================================================================
# Verdicts
# ==========================================================================

def gate_passed(res: dict) -> bool | None:
    g = res.get("gate")
    if g is None:
        return None
    return g["fwd_mse"] <= GATE_RATIO * g["nochange_mse"]


def run_passes(res: dict, hypothesis: str) -> bool | None:
    """Does this run support the hypothesis? None = not applicable (H3b)."""
    if res.get("missing"):
        return False
    if res["spec"]["variant"] in ("FULL", "NOEFF") and not gate_passed(res):
        return False
    if hypothesis.startswith("H3b") and not passes(res["effects"]["H3b_applicable_spont_minus_other"]):
        return None
    return passes(res["effects"][hypothesis])


def verdicts(results: list[dict]) -> dict:
    by_variant = {v: [r for r in results if r["spec"]["variant"] == v] for v in REGISTERED}
    out = {}
    for variant in ("FULL", "UNTRAINED"):
        rows = by_variant[variant]
        for h in HYPOTHESES:
            flags = [run_passes(r, h) for r in rows]
            n_pass = sum(f is True for f in flags)
            n_na = sum(f is None for f in flags)
            if h.startswith("H3b") and len(rows) - n_na < SUPPORT_MIN:
                verdict = "not applicable"
            else:
                verdict = "supported" if n_pass >= SUPPORT_MIN else "not supported"
            out[f"{variant}:{h}"] = {"passing_runs": n_pass, "not_applicable": n_na,
                                     "runs": len(rows), "verdict": verdict}
    comp = next(r for r in results if r["spec"]["variant"] == "COMPARATOR")
    fooled = [h for h in HYPOTHESES[:3] if out[f"UNTRAINED:{h}"]["verdict"] == "supported"]
    out["V1_untrained_not_fooled"] = {"ok": not fooled, "fooled_by_untrained": fooled}
    out["V2_comparator_passes_H1_H2"] = {
        "ok": passes(comp["effects"]["H1_spont_minus_self"])
        and passes(comp["effects"]["H2_omit_minus_noevent"])}
    nochange = next(r for r in results if r["spec"]["variant"] == "NO-CHANGE")
    out["V3_position_rule_accuracy"] = {k: v for k, v in nochange["attribution"].items()
                                        if k.startswith("position:")}
    return out


# ==========================================================================
# Output
# ==========================================================================

def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _m(m: Metric) -> dict:
    return {"mean": m.mean, "ci_low": m.ci_low, "ci_high": m.ci_high, "n": m.n}


def save_tables(results: list[dict], out: Path) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = {k: [] for k in (
        "runs", "hypotheses", "relpe", "attribution", "t2_trials", "t1_trials",
        "t1_behaviour", "ecological", "probes")}
    for r in results:
        spec = r["spec"]
        ident = {"label": spec["label"], "variant": spec["variant"], "seed": spec["seed"]}
        if r.get("missing"):
            tables["runs"].append({**ident, "missing": True})
            continue
        run_row = {**ident, "missing": False, "eval_seconds": round(r["seconds"], 1)}
        if "gate" in r:
            run_row.update({k: r["gate"][k] for k in ("fwd_mse", "nochange_mse",
                                                       "survived_frac", "survival_s")})
            run_row["fwd_over_nochange"] = r["gate"]["fwd_mse"] / r["gate"]["nochange_mse"]
            run_row["gate_passed"] = gate_passed(r)
        tables["runs"].append(run_row)
        for name, m in r.get("effects", {}).items():
            tables["hypotheses"].append({**ident, "effect": name, **_m(m), "ci_excludes_0": passes(m),
                                         "counts_for_verdict": run_passes(r, name)
                                         if name in HYPOTHESES else ""})
        for cond, m in r.get("relpe", {}).items():
            tables["relpe"].append({**ident, "condition": cond, **_m(m)})
        for k, v in r.get("attribution", {}).items():
            rule, cond = k.split(":")
            tables["attribution"].append({**ident, "rule": rule, "condition": cond, "accuracy": v})
        tables["t2_trials"] += [{**ident, **row} for row in r.get("t2_rows", [])]
        tables["t1_trials"] += [{**ident, **row} for row in r.get("t1_rows", [])]
        tables["t1_behaviour"] += [{**ident, **row} for row in r.get("t1_behaviour", [])]
        tables["ecological"] += [{**ident, "cause": c, "rel_pe": v} for c, v in r.get("ecological", [])]
        probe_label = "RAW-INPUT" if spec["variant"] == "NO-CHANGE" else spec["label"]
        for k, v in r.get("probes", {}).items():
            probe, lag = k.split("@")
            tables["probes"].append({"label": probe_label, "variant": "RAW-INPUT"
                                     if spec["variant"] == "NO-CHANGE" else spec["variant"],
                                     "seed": spec["seed"], "probe": probe, "lag": int(lag),
                                     "accuracy": v})
    for name, rows in tables.items():
        _write(out / f"{name}.csv", rows)
    return tables


def load_tables(out: Path) -> dict[str, list[dict]]:
    names = ("runs", "hypotheses", "relpe", "attribution", "t2_trials", "t1_trials",
             "t1_behaviour", "ecological", "probes")
    return {n: list(csv.DictReader((out / f"{n}.csv").open())) if (out / f"{n}.csv").exists()
            else [] for n in names}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--models", type=Path, default=Path("results/v02/models"))
    p.add_argument("--out", type=Path, default=Path("results/v02"))
    p.add_argument("--trials", type=int, default=TRIALS_PER_CONDITION)
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--world", default="agency",
                   help="training world of the agents (free-running episodes use it)")
    p.add_argument("--replot", action="store_true",
                   help="only redraw figures and report from the saved tables")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    from experiments import plots_v02, report_v02
    if args.replot:
        tables = load_tables(args.out)
        v = json.loads((args.out / "verdicts.json").read_text())
        meta = json.loads((args.out / "meta.json").read_text())
        plots_v02.make_all(tables, args.models, args.out)
        report_v02.write(tables, v, meta["spont_step"], args.out, meta.get("world", "agency"))
        print(f"redrew figures and report in {args.out}/")
        return
    t0 = time.perf_counter()
    spont_step = self_event_step()
    specs = predictor_specs(args.models)
    specs.append({"label": "REFLEX", "variant": "REFLEX", "seed": None, "path": None})
    jobs = [(s, spont_step, args.trials, args.world) for s in specs]
    results = []
    with get_context("fork").Pool(args.workers) as pool:
        for res in pool.imap_unordered(evaluate, jobs):
            print(f"  {res['spec']['label']:18s} {res.get('seconds', 0):6.1f} s"
                  f"{'  (missing model)' if res.get('missing') else ''}", flush=True)
            results.append(res)
    order = {s["label"]: i for i, s in enumerate(specs)}
    results.sort(key=lambda r: order[r["spec"]["label"]])
    tables = save_tables(results, args.out)
    v = verdicts([r for r in results if r["spec"]["variant"] != "REFLEX"])
    (args.out / "verdicts.json").write_text(json.dumps(v, indent=2, default=str) + "\n")
    (args.out / "meta.json").write_text(json.dumps(
        {"spont_step": spont_step, "trials_per_condition": args.trials,
         "models": str(args.models), "world": args.world}, indent=2) + "\n")
    plots_v02.make_all(tables, args.models, args.out)
    report_v02.write(tables, v, spont_step, args.out, args.world)
    print(json.dumps(v, indent=2, default=str))
    print(f"total {time.perf_counter() - t0:.0f} s; outputs in {args.out}/")


if __name__ == "__main__":
    main()
