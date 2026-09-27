"""POST-HOC: forward-model competence on the channels the agency test uses.

The pre-registered competence gate compares the forward model's error with the
NO-CHANGE predictor averaged over all 26 observation channels, some of which
(the efference copy) are trivially predictable from the action. The agency test
itself scores only the eight distal heat channels. This script replays the same
20 held-out gate episodes (same seeds, deterministic policy) and reports the
error ratio (forward model / NO-CHANGE) for all channels (this reproduces the
gate), for all channels except the efference copy, and for the heat channels.

Usage (from the repository root):
    python -m experiments.thermal_competence
"""
from __future__ import annotations

import argparse
import csv
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import torch

from agents.recurrent import RecurrentAgent, load_model
from arena.agency import OBS_INDEX, THERMAL_SLICE, AgencyArena
from experiments.run_v02 import GATE_EPISODES

GATE_SEED0 = 900_000                   # as in experiments/run_v02.py
GATE_RATIO = 0.8
EFFERENCE = [OBS_INDEX["prev_action_x"], OBS_INDEX["prev_action_y"]]
STUDIES = {"Study 2": ("results/v02/models", "agency"), "Study 2b": ("results/v02b/models", "agency_b")}


def job(args) -> dict:
    study, path, world = args
    torch.set_num_threads(1)
    net, _ = load_model(Path(path))
    agent = RecurrentAgent(net)
    keep = np.ones(len(OBS_INDEX), dtype=bool)
    keep[EFFERENCE] = False
    sums = {k: [0.0, 0.0] for k in ("all", "no_efference", "thermal")}
    for ep in range(GATE_EPISODES):
        env = AgencyArena(world, seed=GATE_SEED0 + ep)
        obs, info = env.reset()
        agent.reset()
        done = False
        while not done:
            action = agent.act(obs, info)
            pred = agent.predict_next(action)
            prev = obs
            obs, _, term, trunc, info = env.step(action)
            e, c = (pred - obs) ** 2, (prev - obs) ** 2
            for key, sel in (("all", slice(None)), ("no_efference", keep), ("thermal", THERMAL_SLICE)):
                sums[key][0] += float(e[sel].mean())
                sums[key][1] += float(c[sel].mean())
            done = term or trunc
    return {"study": study, "run": Path(path).stem,
            **{f"ratio_{k}": v[0] / v[1] for k, v in sums.items()}}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", type=Path, default=Path("results/thermal_competence"))
    p.add_argument("--workers", type=int, default=12)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    jobs = [(study, str(f), world) for study, (d, world) in STUDIES.items()
            for f in sorted(Path(d).glob("*.pt")) if f.stem.split("_")[0] in ("FULL", "NOEFF")]
    with get_context("fork").Pool(args.workers) as pool:
        rows = sorted(pool.map(job, jobs), key=lambda r: (r["study"], r["run"]))
    with (args.out / "thermal_competence.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    lines = ["# POST-HOC: forward-model competence on the heat channels", "",
             f"Forward-model error / NO-CHANGE error on the {GATE_EPISODES} held-out gate episodes "
             f"(seeds {GATE_SEED0}+). Below {GATE_RATIO} = passes the pre-registered gate threshold; "
             "below 1 = better than predicting no change.", "",
             "| Study | Run | All channels (the gate) | Without efference copy | Heat channels (what T2 scores) |",
             "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['study']} | {r['run']} | {r['ratio_all']:.2f} | {r['ratio_no_efference']:.2f} | "
                     f"{r['ratio_thermal']:.2f} |")
    (args.out / "thermal_competence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
