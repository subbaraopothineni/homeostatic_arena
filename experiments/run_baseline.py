"""Run every baseline agent through every marker test and save CSVs and figures.

Usage (from the repository root):
    python -m experiments.run_baseline --seeds 30 --out results/
"""
from __future__ import annotations

import argparse
import csv
import functools
import math
import time
from pathlib import Path

from agents import AGENT_NAMES, ALL_AGENT_NAMES, make_agent
from arena.scenarios import foraging, tradeoff
from experiments import plots
from experiments.markers import (
    TRADEOFF_START_ENERGIES,
    Metric,
    anticipation_marker,
    format_design_check,
    run_foraging,
    sensitization_marker,
    survival_marker,
    tradeoff_design_check,
    tradeoff_marker,
)

# Metrics shown in the terminal table (all metrics go to summary.csv).
TABLE_METRICS = [
    ("survival", "survived_frac"),
    ("survival", "survival_time_s"),
    ("survival", "time_on_charger_s"),
    ("survival", "damage_taken"),
    ("anticipation", "anticipation_rate"),
    ("anticipation", "anticipation_rate_pooled"),
    ("anticipation", "encounters_per_episode"),
    ("anticipation", "peak_ambient_per_encounter_c"),
    ("tradeoff", "crossing_rate@{lo}"),
    ("tradeoff", "crossing_rate@{hi}"),
    ("tradeoff", "tradeoff_score"),
    ("tradeoff", "tradeoff_score_entry"),
    ("tradeoff", "tradeoff_score_given_approach"),
    ("tradeoff", "logistic_slope"),
    ("tradeoff", "reached_charger@{lo}"),
    ("tradeoff", "reached_charger@{hi}"),
    ("sensitization", "sensitization_c"),
    ("sensitization", "sensitization_nonharmful_c"),
    ("sensitization", "episodes_with_harm"),
]


def fmt_metric(m: Metric) -> str:
    if math.isnan(m.mean):
        return f"n/a (n={m.n})"
    if math.isnan(m.ci_low):
        return f"{m.mean:.3g} (n={m.n})"
    return f"{m.mean:.3g} [{m.ci_low:.3g}, {m.ci_high:.3g}] n={m.n}"


def write_csv(path: Path, rows: list[dict]) -> None:
    columns: list[str] = []
    for row in rows:
        columns += [k for k in row if k not in columns]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=30, help="episodes per condition")
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--agents", nargs="+", default=list(AGENT_NAMES),
                        choices=ALL_AGENT_NAMES, help="agents to run (default: baseline set)")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t_start = time.perf_counter()

    check = tradeoff_design_check(TRADEOFF_START_ENERGIES)
    check_text = format_design_check(check)
    print(check_text, "\n")
    (args.out / "design_check.txt").write_text(check_text + "\n")

    summary: dict[str, dict[str, Metric]] = {}
    marker_of: dict[str, str] = {}
    episode_rows: list[dict] = []
    foraging_logs, tradeoff_logs = {}, {}

    for agent in args.agents:
        t0 = time.perf_counter()
        factory = functools.partial(make_agent, agent)
        logs = run_foraging(factory, args.seeds, agent_name=agent)
        results = {
            "survival": survival_marker(logs=logs),
            "anticipation": anticipation_marker(logs=logs),
            "sensitization": sensitization_marker(logs=logs),
            "tradeoff": tradeoff_marker(factory, args.seeds, agent_name=agent),
        }
        summary[agent] = {}
        for marker, res in results.items():
            summary[agent].update(res.metrics)
            marker_of.update({k: marker for k in res.metrics})
        episode_rows += results["survival"].episodes + results["tradeoff"].episodes
        foraging_logs[agent] = logs
        tradeoff_logs[agent] = results["tradeoff"].logs
        print(f"{agent:22s} done in {time.perf_counter() - t0:5.1f} s")

    # ---------------------------------------------------------------- CSVs
    summary_rows = [
        {"agent": agent, "marker": marker_of[name], "metric": name, "mean": m.mean,
         "ci_low": m.ci_low, "ci_high": m.ci_high, "n": m.n}
        for agent, metrics in summary.items() for name, m in metrics.items()
    ]
    write_csv(args.out / "summary.csv", summary_rows)
    write_csv(args.out / "episodes.csv", episode_rows)

    # ---------------------------------------------------------------- figures
    lo, hi = min(TRADEOFF_START_ENERGIES), max(TRADEOFF_START_ENERGIES)
    plots.plot_trajectories_foraging(foraging_logs, foraging(),
                                     args.out / "trajectories_foraging.png")
    plots.plot_trajectories_tradeoff(tradeoff_logs, {lo: tradeoff(lo), hi: tradeoff(hi)},
                                     args.out / "trajectories_tradeoff.png")
    plots.plot_markers(summary, args.out / "markers.png", lo, hi)
    plots.plot_tradeoff_by_energy(summary, TRADEOFF_START_ENERGIES,
                                  args.out / "tradeoff_by_energy.png")
    # Trace: a nociceptive-reflex foraging episode (it is the agent that actually
    # gets heated), the one with the most heat encounters including >= 1 harmful.
    trace_agent = next((a for a in args.agents if "nociceptive" in a), args.agents[0])
    by_seed = {r["seed"]: r for r in results_rows(episode_rows, trace_agent)}
    candidates = [lg for lg in foraging_logs[trace_agent] if by_seed[lg.seed]["n_harmful"] > 0]
    trace_log = max(candidates, key=lambda lg: by_seed[lg.seed]["n_encounters"],
                    default=foraging_logs[trace_agent][0])
    plots.plot_physiology_trace(trace_log, args.out / "physiology_trace.png")

    # ---------------------------------------------------------------- table
    width = 38
    print("\n" + "metric".ljust(width) + "".join(a.ljust(40) for a in summary))
    for marker, name in TABLE_METRICS:
        key = name.format(lo=lo, hi=hi)
        print(f"{marker[:5]}:{key}".ljust(width)
              + "".join(fmt_metric(summary[a][key]).ljust(40) for a in summary))
    print(f"\nTotal runtime {time.perf_counter() - t_start:.1f} s; outputs in {args.out}/")


def results_rows(rows: list[dict], agent: str) -> list[dict]:
    """Foraging-episode rows for one agent."""
    return [r for r in rows if r["agent"] == agent and r["scenario"] == "foraging"]


if __name__ == "__main__":
    main()
