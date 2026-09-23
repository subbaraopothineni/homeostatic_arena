"""POST-HOC sensitivity analysis for the Study 2 agency test (not pre-registered).

Question: how large a self-prediction effect would the pre-registered test have
detected? Each trained FULL agent's distal-heat predictions are blended with the
hand-built comparator's:

    prediction = (1 - w) * agent + w * comparator      (heat channels only)

so the blended predictor anticipates roughly a fraction w of a self-caused lamp
change and keeps the agent's own noise and biases. The identical T2 battery and
pass rule (CI excludes 0 in >= 4 of 5 runs, competence gate applied) are run for
each w.

Usage (from the repository root):
    python -m experiments.sensitivity_v02 --models results/v02/models --out results/v02
"""
from __future__ import annotations

import argparse
import csv
import json
from multiprocessing import get_context
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

from agents.recurrent import load_model  # noqa: E402
from arena.agency import THERMAL_SLICE, AgencyArena  # noqa: E402
from experiments.agency_tests import (  # noqa: E402
    ComparatorPredictor,
    NetworkPredictor,
    Predictor,
    hypothesis_effects,
    passes,
    run_t2,
)
from experiments.plots import INK, INK_2  # noqa: E402
from experiments.plots_v02 import COLORS  # noqa: E402

WEIGHTS = (0.0, 0.02, 0.05, 0.1, 0.25, 0.5)
HYPS = ("H1_spont_minus_self", "H2_omit_minus_noevent", "H3a_selfblind_interaction")
SUPPORT_MIN = 4


class BlendPredictor(Predictor):
    """Agent forward model with a fraction w of the comparator's heat prediction."""

    def __init__(self, net, w: float):
        self.agent = NetworkPredictor(net, "blend")
        self.comparator = ComparatorPredictor()
        self.w = w

    def bind(self, env: AgencyArena) -> None:
        self.comparator.bind(env)

    def reset(self) -> None:
        self.agent.reset()

    def observe(self, obs) -> None:
        self.agent.observe(obs)
        self.comparator.observe(obs)

    def predict_next(self, action):
        pred = self.agent.predict_next(action)
        comp = self.comparator.predict_next(action)
        pred[THERMAL_SLICE] = (1 - self.w) * pred[THERMAL_SLICE] + self.w * comp[THERMAL_SLICE]
        return pred

    def state(self):
        return self.agent.state()


def job(args) -> list[dict]:
    seed, w, models, spont_step, trials = args
    torch.set_num_threads(1)
    net, _ = load_model(models / f"FULL_seed{seed}.pt")
    effects = hypothesis_effects(run_t2(lambda: BlendPredictor(net, w), spont_step, trials))
    return [{"w": w, "seed": seed, "hypothesis": h, "mean": effects[h].mean,
             "ci_low": effects[h].ci_low, "ci_high": effects[h].ci_high,
             "ci_excludes_0": passes(effects[h])} for h in HYPS]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--models", type=Path, default=Path("results/v02/models"))
    p.add_argument("--out", type=Path, default=Path("results/v02"))
    p.add_argument("--trials", type=int, default=40)
    p.add_argument("--workers", type=int, default=12)
    args = p.parse_args()
    spont_step = json.loads((args.out / "meta.json").read_text())["spont_step"]
    runs = {r["label"]: r for r in csv.DictReader((args.out / "runs.csv").open())}
    gate_ok = {s: runs[f"FULL_seed{s}"].get("gate_passed") == "True" for s in range(5)}
    jobs = [(s, w, args.models, spont_step, args.trials) for w in WEIGHTS for s in range(5)]
    rows: list[dict] = []
    with get_context("fork").Pool(args.workers) as pool:
        for r in pool.imap_unordered(job, jobs):
            rows += r
    rows.sort(key=lambda r: (r["w"], r["seed"], r["hypothesis"]))
    for r in rows:
        r["gate_passed"] = gate_ok[r["seed"]]
        r["counts"] = r["ci_excludes_0"] and r["gate_passed"]
    with (args.out / "sensitivity.csv").open("w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w_.writeheader()
        w_.writerows(rows)

    # Table and verdict per weight
    lines = ["# POST-HOC sensitivity of the Study 2 agency test (not pre-registered)", "",
             "Blended predictor = (1 − w) × trained FULL agent + w × hand-built comparator "
             "(heat channels). Same T2 battery, 40 trials per condition, same pass rule "
             "(≥ 4 of 5 runs; FULL_seed4 fails the competence gate and never counts).", "",
             "| w | H1 effect (mean of 5 runs) | H1 runs passing | H2 runs passing | "
             "H3a runs passing | Would H1 be declared supported? |", "|---|---|---|---|---|---|"]
    summary = {}
    for w in WEIGHTS:
        sel = [r for r in rows if r["w"] == w]
        n = {h: sum(r["counts"] for r in sel if r["hypothesis"] == h) for h in HYPS}
        h1 = np.mean([r["mean"] for r in sel if r["hypothesis"] == HYPS[0]])
        summary[w] = (h1, n)
        lines.append(f"| {w} | {h1:+.3f} | {n[HYPS[0]]}/5 | {n[HYPS[1]]}/5 | {n[HYPS[2]]}/5 | "
                     f"{'yes' if n[HYPS[0]] >= SUPPORT_MIN else 'no'} |")
    detect = [w for w in WEIGHTS if summary[w][1][HYPS[0]] >= SUPPORT_MIN]
    actual = [r for r in csv.DictReader((args.out / "hypotheses.csv").open())
              if r["variant"] == "FULL" and r["effect"] == HYPS[0]]
    upper = max(float(r["ci_high"]) for r in actual)
    lines += ["",
              f"**Smallest blend weight detected by the pre-registered rule:** "
              f"{min(detect) if detect else 'none tested'}.",
              f"**Equivalence bound from the actual data:** every FULL run's H1 95% CI lies "
              f"below +{upper:.3f} (relative prediction error units).", "",
              "![sensitivity](fig_sensitivity.png)", ""]
    (args.out / "sensitivity.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
    for seed in range(5):
        pts = [(r["w"], r["mean"]) for r in rows if r["seed"] == seed and r["hypothesis"] == HYPS[0]]
        axes[0].plot(*zip(*pts), "o-", color=COLORS["FULL"], alpha=0.8, ms=5, lw=1.2)
    axes[0].axhline(upper, color=INK_2, lw=1.0)
    axes[0].annotate("largest CI bound in the real data", (0.0, upper), xytext=(4, 4),
                     textcoords="offset points", fontsize=8, color=INK_2)
    axes[0].set_xscale("symlog", linthresh=0.02)
    axes[0].set_xticks(list(WEIGHTS), [f"{w:g}" for w in WEIGHTS])
    axes[0].set_xlabel("blend weight w (fraction of the comparator mixed in)")
    axes[0].set_ylabel("H1 effect: relPE(SPONT) − relPE(SELF)")
    axes[0].set_title("Effect size grows with w (one line per FULL run)", loc="left")
    for h, marker in zip(HYPS, ("o", "s", "^")):
        axes[1].plot(list(WEIGHTS), [summary[w][1][h] for w in WEIGHTS], marker + "-",
                     color=INK, ms=6, lw=1.2, label=h.split("_")[0])
    axes[1].axhline(SUPPORT_MIN, color=INK_2, lw=1.0)
    axes[1].set_xscale("symlog", linthresh=0.02)
    axes[1].set_xticks(list(WEIGHTS), [f"{w:g}" for w in WEIGHTS])
    axes[1].set_ylim(-0.2, 5.2)
    axes[1].set_xlabel("blend weight w")
    axes[1].set_ylabel("runs counting toward the verdict (of 5)")
    axes[1].set_title("Pass rule needs ≥ 4 (line)", loc="left")
    axes[1].legend(loc="center right")
    fig.suptitle("POST-HOC: how sensitive is the pre-registered agency test?", color=INK)
    fig.savefig(args.out / "fig_sensitivity.png", dpi=130)
    plt.close(fig)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
