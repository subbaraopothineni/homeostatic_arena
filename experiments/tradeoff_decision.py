"""POST-HOC: the motivational trade-off measured at the moment of decision.

The pre-specified trade-off score compares crossing rates between *start*
energies (0.08 vs 0.9). Energy drains during the 90 s episode, so an agent that
starts at 0.9 can be in need later and cross then; the score then credits the
crossing to "high energy". This analysis instead scores each approach to the
wall: the agent's energy when the approach begins (ambient > 38 C on the west
side, i.e. on the way to the charger) and whether it crossed through the wall
during that approach. A negative logistic slope of crossing on energy (with a
95% CI below 0; bootstrap over episodes) is the trade-off signature: the agent
accepts the noxious route when, and only when, it is in need.

Usage (from the repository root):
    python -m experiments.tradeoff_decision --seeds 100 --out results/minimal_controls
"""
from __future__ import annotations

import argparse
import csv
import functools
import math
from pathlib import Path

import numpy as np

from agents import make_agent
from arena.scenarios import tradeoff
from experiments.markers import (
    TRADEOFF_START_ENERGIES,
    crossed_through_wall,
    find_encounters,
    fit_logistic,
    run_episode,
)

AGENTS = ("random", "reflex_nociceptive", "reflex_thermotactic", "reflex_motivational",
          "reflex_sensitizing")
BINS = ((0.0, 0.25), (0.25, 0.5), (0.5, 1.01))
N_BOOT = 2000


def approaches(log, half_len: float) -> list[tuple[float, bool]]:
    """(energy at the start of each westward-side wall approach, crossed during it)."""
    d = log.data
    out = []
    for enc in find_encounters(d["ambient_c"], d["nociceptor"]):
        if d["x"][enc.start] >= 0:          # approach from the charger side: not a decision to cross
            continue
        sl = slice(max(enc.start - 1, 0), enc.end)
        out.append((float(d["energy"][enc.start]), crossed_through_wall(d["x"][sl], d["y"][sl], half_len)))
    return out


def slope_ci(episodes: list[list[tuple[float, bool]]], seed: int = 0) -> tuple[float, float, float]:
    pts = [p for ep in episodes for p in ep]
    if not pts or not any(c for _, c in pts) or all(c for _, c in pts):
        return math.nan, math.nan, math.nan
    x = np.array([e for e, _ in pts])
    y = np.array([float(c) for _, c in pts])
    slope = fit_logistic(x, y)[1]
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(episodes), len(episodes))
        bp = [p for i in idx for p in episodes[i]]
        bx = np.array([e for e, _ in bp])
        by = np.array([float(c) for _, c in bp])
        if 0 < by.sum() < len(by):
            boots.append(fit_logistic(bx, by)[1])
    boots = [b for b in boots if math.isfinite(b)]
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (math.nan, math.nan)
    return float(slope), float(lo), float(hi)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seeds", type=int, default=100)
    p.add_argument("--out", type=Path, default=Path("results/minimal_controls"))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows, lines = [], ["# POST-HOC: trade-off measured at the moment of decision", "",
                       f"Trade-off world, start energies {TRADEOFF_START_ENERGIES}, {args.seeds} seeds each. "
                       "One observation per approach to the wall from the start side; energy is the "
                       "agent's energy when the approach began. Slope: logistic regression of crossing "
                       "on energy (negative = crosses when in need), 95% CI from a bootstrap over episodes.", "",
                       "| Agent | Approaches | Crossed | P(cross), energy < 0.25 | 0.25–0.5 | ≥ 0.5 | "
                       "Logistic slope [95% CI] |", "|---|---|---|---|---|---|---|"]
    for agent in AGENTS:
        factory = functools.partial(make_agent, agent)
        episodes = []
        for e in TRADEOFF_START_ENERGIES:
            scen = tradeoff(e)
            for seed in range(args.seeds):
                episodes.append(approaches(run_episode(factory, scen, seed, agent),
                                           scen.extra["wall_half_length"]))
        pts = [pt for ep in episodes for pt in ep]
        binned = []
        for lo, hi in BINS:
            sel = [c for en, c in pts if lo <= en < hi]
            binned.append((sum(sel), len(sel)))
        slope, s_lo, s_hi = slope_ci(episodes)
        rows.append({"agent": agent, "approaches": len(pts), "crossed": sum(c for _, c in pts),
                     **{f"cross_{lo}_{hi}": f"{k}/{n}" for (lo, hi), (k, n) in zip(BINS, binned)},
                     "slope": slope, "slope_ci_low": s_lo, "slope_ci_high": s_hi})
        fmt = lambda k, n: f"{k / n:.2f} ({k}/{n})" if n else "—"  # noqa: E731
        sl = "no crossings" if not sum(c for _, c in pts) else f"{slope:+.1f} [{s_lo:+.1f}, {s_hi:+.1f}]"
        lines.append(f"| {agent} | {len(pts)} | {sum(c for _, c in pts)} | "
                     f"{' | '.join(fmt(k, n) for k, n in binned)} | {sl} |")
    with (args.out / "tradeoff_decision.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (args.out / "tradeoff_decision.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
