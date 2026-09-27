"""POST-HOC: sensitivity of the agency test to an *imprecise* self-prediction.

experiments/sensitivity_v02.py blends each trained agent's heat prediction with
the hand-built comparator's, which times self-caused lamp changes perfectly. A
partly learned self-model would be less precise. Here the comparator is given,
per trial, (a) a misjudgement of the pad edge, radius error ~ N(0, sigma) m,
which shifts the step at which it expects the toggle (the agent moves about
0.08 m per step), and (b) an error in the size of the change it expects, gain ~
lognormal(0, 0.3). The draw depends only on the trial (its start position), so
intact and ablated versions of a trial share it. The blend, the T2 battery and
the pass rule are otherwise identical to sensitivity_v02.

Usage (from the repository root):
    python -m experiments.sensitivity_noisy --models results/v02/models --out results/v02
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import torch

from agents.recurrent import load_model
from arena.agency import OBS_INDEX, THERMAL_SLICE
from arena.env import AGENT_MASS_KG, MOTOR_GEAR, SLIDE_DAMPING, VEL_SCALE
from experiments.agency_tests import ComparatorPredictor, hypothesis_effects, passes, run_t2
from experiments.sensitivity_v02 import HYPS, SUPPORT_MIN, BlendPredictor

WEIGHTS = (0.02, 0.05, 0.1, 0.25, 0.5, 1.0)
LEVELS = {"exact": (0.0, 0.0), "edge error 0.05 m": (0.05, 0.3),
          "edge error 0.1 m": (0.1, 0.3), "edge error 0.2 m": (0.2, 0.3)}


class NoisyComparator(ComparatorPredictor):
    """The comparator with a per-trial pad-edge misjudgement and gain error."""
    name = "NOISY-COMPARATOR"

    def __init__(self, sigma_m: float, gain_sd: float, seed: int):
        self.sigma_m, self.gain_sd, self.seed = sigma_m, gain_sd, seed

    def bind(self, env) -> None:
        super().bind(env)
        self._draw = None

    def observe(self, obs):
        if self._draw is None:          # first observation of the trial: its start position
            key = [self.seed] + [int(round(float(obs[OBS_INDEX[c]]) * 1e6)) % 2**32 for c in ("pos_x", "pos_y")]
            rng = np.random.default_rng(key)
            self._draw = (rng.normal(0.0, self.sigma_m) if self.sigma_m else 0.0,
                          math.exp(rng.normal(0.0, self.gain_sd)) if self.gain_sd else 1.0)
        super().observe(obs)

    def predict_next(self, action):
        dr, gain = self._draw
        pred = self._obs.copy()
        env = self.env
        h = env.scenario.half_size
        pos = np.array([self._obs[OBS_INDEX["pos_x"]], self._obs[OBS_INDEX["pos_y"]]]) * h
        vel = np.array([self._obs[OBS_INDEX["vel_x"]], self._obs[OBS_INDEX["vel_y"]]]) * VEL_SCALE
        tau = AGENT_MASS_KG / SLIDE_DAMPING
        v_term = MOTOR_GEAR / SLIDE_DAMPING * np.clip(np.asarray(action, float), -1, 1)
        next_pos = pos + v_term * env.dt + (vel - v_term) * tau * (1 - math.exp(-env.dt / tau))
        r = max(env.pad_radius + dr, 0.01)
        base = env.thermal_vision(next_pos)
        if math.dist(pos, env.pad_xy) >= r > math.dist(next_pos, env.pad_xy):
            env._set_lamp(not env.lamp_on)
            toggled = env.thermal_vision(next_pos)
            env._set_lamp(not env.lamp_on)
            pred[THERMAL_SLICE] = base + gain * (toggled - base)
        else:
            pred[THERMAL_SLICE] = base
        return pred


class NoisyBlend(BlendPredictor):
    def __init__(self, net, w: float, sigma_m: float, gain_sd: float, seed: int):
        super().__init__(net, w)
        self.comparator = NoisyComparator(sigma_m, gain_sd, seed)


def job(args) -> list[dict]:
    level, w, seed, models, spont_step, trials = args
    torch.set_num_threads(1)
    net, _ = load_model(models / f"FULL_seed{seed}.pt")
    sigma, gain_sd = LEVELS[level]
    effects = hypothesis_effects(run_t2(lambda: NoisyBlend(net, w, sigma, gain_sd, 7919 + seed),
                                        spont_step, trials))
    return [{"level": level, "w": w, "seed": seed, "hypothesis": hyp, "mean": effects[hyp].mean,
             "ci_low": effects[hyp].ci_low, "ci_high": effects[hyp].ci_high,
             "ci_excludes_0": passes(effects[hyp])} for hyp in HYPS]


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
    jobs = [(lv, w, s, args.models, spont_step, args.trials) for lv in LEVELS for w in WEIGHTS for s in range(5)]
    rows: list[dict] = []
    with get_context("fork").Pool(args.workers) as pool:
        for r in pool.imap_unordered(job, jobs):
            rows += r
    order = list(LEVELS)
    rows.sort(key=lambda r: (order.index(r["level"]), r["w"], r["seed"], r["hypothesis"]))
    for r in rows:
        r["gate_passed"] = gate_ok[r["seed"]]
        r["counts"] = r["ci_excludes_0"] and r["gate_passed"]
    with (args.out / "sensitivity_noisy.csv").open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)

    lines = ["# POST-HOC: sensitivity to an imprecise self-prediction (not pre-registered)", "",
             "Blended predictor = (1 − w) × trained FULL agent + w × comparator with a per-trial pad-edge "
             "error ~ N(0, σ) and gain error ~ lognormal(0, 0.3). Runs meeting each hypothesis "
             "(CI excludes 0; gated-out FULL seed 4 never counts; pass rule ≥ 4 of 5). "
             "In brackets: H1 runs with CI > 0 ignoring the gate.", "",
             "| Self-model precision | " + " | ".join(f"w = {w:g}" for w in WEIGHTS) + " |",
             "|---|" + "---|" * len(WEIGHTS)]
    for lv in LEVELS:
        cells = []
        for w in WEIGHTS:
            sel = [r for r in rows if r["level"] == lv and r["w"] == w]
            n = {h: sum(r["counts"] for r in sel if r["hypothesis"] == h) for h in HYPS}
            raw = sum(r["ci_excludes_0"] for r in sel if r["hypothesis"] == HYPS[0])
            h1 = np.mean([r["mean"] for r in sel if r["hypothesis"] == HYPS[0]])
            cells.append(f"H1 {n[HYPS[0]]}/5 ({raw}), H2 {n[HYPS[1]]}/5, H3a {n[HYPS[2]]}/5; effect {h1:+.3f}")
        lines.append(f"| {lv} | " + " | ".join(cells) + " |")
    (args.out / "sensitivity_noisy.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
