"""EXPLORATORY (not pre-registered) follow-up analyses for Study 2.

Written after the pre-registered analysis came out negative, to understand why.
Results from this script must be reported as exploratory.

1. Reafference: does the agent predict the change in its distal heat sense that
   its own movement causes (the static hot spot shifting direction as it walks)?
   Measured on NOEVENT trials (no lamp change) as thermal prediction error divided
   by the error of predicting no change, during the motion phase, with self-motion
   signals intact or frozen (self-blind). The stationary warm-up gives the noise
   floor.
2. Event statistics: how often each cause toggled the lamp in the free-running
   episodes of the ecological check.
3. Strategy: what survival strategy the FULL agents learned (charging with the
   lamp off, waiting, using the switch), in 20 fresh free-running episodes.

Usage (from the repository root):
    python -m experiments.explore_v02 --models results/v02/models --out results/v02
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from multiprocessing import get_context
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from agents.recurrent import RecurrentAgent, load_model  # noqa: E402
from arena.agency import AgencyArena  # noqa: E402
from experiments.agency_tests import (  # noqa: E402
    WARMUP_STEPS,
    ComparatorPredictor,
    NetworkPredictor,
    NoChangePredictor,
    run_t2_trial,
)
from experiments.markers import bootstrap_mean  # noqa: E402
from experiments.plots import INK, INK_2  # noqa: E402
from experiments.plots_v02 import COLORS  # noqa: E402
from experiments.run_v02 import predictor_specs  # noqa: E402

TRIALS = 40


def _ratios(trials, phase: str) -> list[float]:
    out = []
    for t in trials:
        if phase == "motion":
            steps = [e for e in t.step_errors if WARMUP_STEPS <= e[0] < t.event_step]
        else:
            steps = [e for e in t.step_errors if 0 < e[0] < WARMUP_STEPS]
        err, base = sum(e[1] for e in steps), sum(e[2] for e in steps)
        out.append(err / base if base > 0 else float("nan"))
    return out


def reafference(job) -> list[dict]:
    spec, spont_step = job
    torch.set_num_threads(1)
    if spec["variant"] == "COMPARATOR":
        factory = ComparatorPredictor
    elif spec["variant"] == "NO-CHANGE":
        factory = NoChangePredictor
    else:
        net, _ = load_model(spec["path"])
        factory = lambda: NetworkPredictor(net, spec["label"])  # noqa: E731
    rows = []
    for ablation in ("none", "self-blind", "other-blind"):
        trials = [run_t2_trial(factory(), "NOEVENT", ablation, i % 2 == 0, i, spont_step)
                  for i in range(TRIALS)]
        for phase in ("static", "motion"):
            if phase == "static" and ablation != "none":
                continue
            m = bootstrap_mean(_ratios(trials, phase))
            rows.append({"label": spec["label"], "variant": spec["variant"], "seed": spec["seed"],
                         "ablation": ablation, "phase": phase, "mean": m.mean,
                         "ci_low": m.ci_low, "ci_high": m.ci_high, "n": m.n})
    return rows


def plot(rows: list[dict], path: Path) -> None:
    groups = ("FULL", "NOEFF", "NOFWD", "UNTRAINED", "COMPARATOR")
    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    for gi, g in enumerate(groups):
        runs = sorted({r["label"] for r in rows if r["variant"] == g})
        for k, run in enumerate(runs):
            def val(abl, phase="motion"):
                return next(float(r["mean"]) for r in rows if r["label"] == run
                            and r["ablation"] == abl and r["phase"] == phase)
            x0 = gi + (k - (len(runs) - 1) / 2) * 0.12
            ax.plot([x0 - 0.03, x0 + 0.03], [val("none"), val("self-blind")], "-",
                    color=COLORS[g], lw=1.2)
            ax.plot(x0 - 0.03, val("none"), "o", color=COLORS[g], ms=6)
            ax.plot(x0 + 0.03, val("self-blind"), "o", color=COLORS[g], ms=6, mfc="white")
            ax.plot(x0 - 0.03, val("other-blind"), "x", color=INK, ms=6, mew=1.5)
    ax.axhline(1.0, color=INK_2, lw=1.0)
    ax.set_xticks(range(len(groups)), groups)
    ax.set_yscale("log")
    ax.set_ylabel("thermal prediction error / no-change error\n(while walking, no lamp change)")
    ax.set_title("EXPLORATORY: does the agent predict how its own movement changes what it "
                 "senses?\nfilled = intact, open = self-blind, x = other-blind (control); "
                 "below 1 = better than predicting no change",
                 loc="left", fontsize=10, color=INK)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def strategy(job) -> dict:
    """What survival strategy did a FULL agent learn? 20 fresh free-running episodes."""
    seed, models, world = job
    torch.set_num_threads(1)
    net, _ = load_model(models / f"FULL_seed{seed}.pt")
    agent = RecurrentAgent(net)
    s = Counter()
    for ep in range(20):
        env = AgencyArena(world, seed=700_000 + 100 * seed + ep)
        obs, info = env.reset()
        agent.reset()
        done = term = False
        while not done:
            obs, _, term, trunc, info = env.step(agent.act(obs, info))
            done = term or trunc
            xy = (info["x"], info["y"])
            s["steps"] += 1
            s["lamp_on"] += info["lamp_on"]
            if info["on_charger"]:
                s["on_charger"] += 1
                s["charger_lamp_off"] += not info["lamp_on"]
            if info["lamp_on"] and 0.6 < math.dist(xy, env.scenario.charger_xy) < 2.0:
                s["waiting_near_charger"] += 1
            for e in info["events"]:
                s[f"toggle_{e['cause']}"] += 1
        s["died"] += term
    n, oc = s["steps"], max(s["on_charger"], 1)
    return {"label": f"FULL_seed{seed}", "lamp_on_pct": 100 * s["lamp_on"] / n,
            "on_charger_pct": 100 * s["on_charger"] / n,
            "charging_with_lamp_off_pct": 100 * s["charger_lamp_off"] / oc if s["on_charger"] else float("nan"),
            "waiting_near_charger_when_lamp_on_pct": 100 * s["waiting_near_charger"] / max(s["lamp_on"], 1),
            "self_toggles_per_ep": s["toggle_self"] / 20, "other_toggles_per_ep": s["toggle_other"] / 20,
            "spontaneous_toggles_per_ep": s["toggle_spontaneous"] / 20, "deaths_of_20": s["died"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--models", type=Path, default=Path("results/v02/models"))
    p.add_argument("--out", type=Path, default=Path("results/v02"))
    p.add_argument("--world", default="agency", help="training world of the agents")
    p.add_argument("--workers", type=int, default=12)
    args = p.parse_args()
    spont_step = json.loads((args.out / "meta.json").read_text())["spont_step"]
    specs = [s for s in predictor_specs(args.models)
             if s["variant"] != "NO-CHANGE" and (s["path"] or s["variant"] == "COMPARATOR")]
    rows: list[dict] = []
    with get_context("fork").Pool(args.workers) as pool:
        for r in pool.imap_unordered(reafference, [(s, spont_step) for s in specs]):
            rows += r
    order = {s["label"]: i for i, s in enumerate(specs)}
    rows.sort(key=lambda r: (order[r["label"]], r["ablation"], r["phase"]))
    with (args.out / "exploratory_reafference.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    plot(rows, args.out / "fig_exploratory_reafference.png")

    eco = list(csv.DictReader((args.out / "ecological.csv").open()))
    counts = {lab: Counter(r["cause"] for r in eco if r["label"] == lab)
              for lab in dict.fromkeys(r["label"] for r in eco)}

    lines = ["# EXPLORATORY analyses for Study 2 (not pre-registered)", "",
             "Written after the pre-registered analysis came out negative, to understand why. "
             "Treat as hypothesis-generating.", "",
             "## 1. Reafference: predicting what its own movement does to its senses", "",
             "Thermal prediction error / no-change error on NOEVENT trials (40 per run). "
             "`static` = stationary warm-up (noise floor); `motion` = walking past the pad.", "",
             "| Run | static (intact) | motion (intact) | motion (self-blind) | motion (other-blind) |",
             "|---|---|---|---|---|"]
    for lab in dict.fromkeys(r["label"] for r in rows):
        def cell(abl, phase):
            r = next(x for x in rows if x["label"] == lab and x["ablation"] == abl
                     and x["phase"] == phase)
            return f"{r['mean']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"
        lines.append(f"| {lab} | {cell('none', 'static')} | {cell('none', 'motion')} | "
                     f"{cell('self-blind', 'motion')} | {cell('other-blind', 'motion')} |")
    lines += ["", "![reafference](fig_exploratory_reafference.png)", "",
              "## 2. How often did each cause toggle the lamp? (50 free-running episodes per FULL run)",
              "", "| Run | self | other | spontaneous |", "|---|---|---|---|"]
    for lab, c in counts.items():
        lines.append(f"| {lab} | {c.get('self', 0)} | {c.get('other', 0)} | "
                     f"{c.get('spontaneous', 0)} |")
    total = sum(counts.values(), Counter())
    lines += ["", f"Total: self {total.get('self', 0)}, other {total.get('other', 0)}, "
              f"spontaneous {total.get('spontaneous', 0)}.", ""]

    with get_context("fork").Pool(5) as pool:
        strat = pool.map(strategy, [(s, args.models, args.world) for s in range(5)
                                    if (args.models / f"FULL_seed{s}.pt").exists()])
    with (args.out / "exploratory_strategy.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(strat[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(strat)
    lines += ["## 3. What survival strategy did the agents learn? (20 fresh episodes per FULL run)",
              "", "| Run | lamp on (% of time) | on charger (%) | charging done with lamp off (%) | "
              "waiting near charger while lamp on (%) | self toggles / episode | "
              "other / episode | spontaneous / episode | deaths of 20 |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in strat:
        lines.append(f"| {r['label']} | {r['lamp_on_pct']:.0f} | {r['on_charger_pct']:.0f} | "
                     f"{r['charging_with_lamp_off_pct']:.0f} | "
                     f"{r['waiting_near_charger_when_lamp_on_pct']:.0f} | "
                     f"{r['self_toggles_per_ep']:.2f} | {r['other_toggles_per_ep']:.2f} | "
                     f"{r['spontaneous_toggles_per_ep']:.2f} | {r['deaths_of_20']} |")
    lines.append("")
    (args.out / "exploratory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
