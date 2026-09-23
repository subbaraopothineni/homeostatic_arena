"""Study 1b report: apply the pre-registered decision rules Q1-Q4
(docs/preregistration_v0.2b.md, Part B) and compare the learned agents with the
Study 1 baselines. No numbers are typed by hand.

Usage (after run_baseline has been run for the learned agents, 30 and 100 seeds):
    python -m experiments.report_study1b
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

BASE30, BASE100 = Path("results/summary.csv"), Path("results/seeds100/summary.csv")
LEARN30, LEARN100 = Path("results/study1b/summary.csv"), Path("results/study1b/seeds100/summary.csv")
OUT = Path("results/study1b/report.md")
BASELINES = ("random", "reflex_nociceptive", "reflex_thermotactic")
MEMORYLESS = ("random", "reflex_nociceptive")       # agents with a sensitization value


def load(path: Path) -> dict[tuple[str, str], dict]:
    if not path.exists():
        return {}
    return {(r["agent"], r["metric"]): r for r in csv.DictReader(path.open())}


def f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def cell(r: dict | None) -> str:
    if r is None or math.isnan(f(r["mean"])):
        return f"n/a (n={r['n']})" if r else ""
    if math.isnan(f(r["ci_low"])):
        return f"{f(r['mean']):.2f} (n={r['n']})"
    return f"{f(r['mean']):.2f} [{f(r['ci_low']):.2f}, {f(r['ci_high']):.2f}]"


def main() -> None:
    b30, b100, l30, l100 = load(BASE30), load(BASE100), load(LEARN30), load(LEARN100)
    learned = sorted({a for a, _ in l30})
    lines = ["# Study 1b: a learning agent on the Study 1 sentience markers", "",
             "Pre-registered in `docs/preregistration_v0.2b.md` (Part B). Deterministic "
             "policy. Baselines from Study 1 (same episode seeds). Functional measurements "
             "only; no claim about subjective experience.", ""]

    # ---------------------------------------------------------------- overview table
    metrics = [("survived_frac", "survived 90 s"), ("anticipation_rate", "anticipation rate"),
               ("crossing_rate@0.08", "crossing @ energy 0.08"),
               ("crossing_rate@0.9", "crossing @ energy 0.9"),
               ("tradeoff_score", "trade-off score"), ("reached_charger@0.08", "reached charger @ 0.08"),
               ("reached_charger@0.9", "reached charger @ 0.9")]
    agents = list(BASELINES) + learned
    lines += ["## Overview (30 seeds per condition; mean [95% CI])", "",
              "| metric | " + " | ".join(agents) + " |", "|---|" + "---|" * len(agents)]
    for key, label in metrics:
        row = [cell(b30.get((a, key)) or l30.get((a, key))) for a in agents]
        lines.append(f"| {label} | " + " | ".join(row) + " |")
    lines.append("")

    # ---------------------------------------------------------------- Q1
    q1 = {a: f(l30[(a, "tradeoff_score")]["ci_low"]) > 0 for a in learned if (a, "tradeoff_score") in l30}
    n1 = sum(q1.values())
    lines += ["## Q1: does the trade-off marker separate the learning agent from the reflexes?", "",
              "Rule: trade-off score > 0 with CI excluding 0 in ≥ 4 of 5 learned seeds "
              "(reflexes scored 0).", ""]
    lines += [f"- {a}: {cell(l30[(a, 'tradeoff_score')])} → {'passes' if ok else 'does not pass'}"
              for a, ok in q1.items()]
    lines += ["", f"**Q1 verdict:** {n1}/{len(q1)} seeds pass → "
              f"{'the trade-off marker separates learner from reflexes' if n1 >= 4 else 'not separated'}.", ""]

    # ---------------------------------------------------------------- Q2
    lines += ["## Q2: anticipatory avoidance (descriptive)", ""]
    lines += [f"- {a}: {cell(l30.get((a, 'anticipation_rate')))}" for a in learned]
    lines += [f"- reflex_thermotactic (Study 1): {cell(b30.get(('reflex_thermotactic', 'anticipation_rate')))}",
              "", "A memoryless reflex already scores 1.00, so this marker cannot discriminate "
              "whatever the learner scores.", ""]

    # ---------------------------------------------------------------- Q3
    lines += ["## Q3: does sensitization separate learning from memoryless agents? (100 seeds)", ""]
    if not l100:
        lines += ["100-seed run not available.", ""]
    else:
        floor = min(f(b100[(a, "sensitization_c")]["ci_low"]) for a in MEMORYLESS)
        q3 = {}
        for a in learned:
            s, s_nh = l100.get((a, "sensitization_c")), l100.get((a, "sensitization_nonharmful_c"))
            if s is None or math.isnan(f(s["ci_high"])) or s_nh is None or math.isnan(f(s_nh["ci_high"])):
                q3[a] = None
            else:
                q3[a] = f(s["ci_high"]) < floor and f(s_nh["ci_high"]) < 0
            lines.append(f"- {a}: sensitization {cell(s)}, non-harmful variant {cell(s_nh)} → "
                         + {None: "not estimable", True: "passes", False: "does not pass"}[q3[a]])
        n3, n_na = sum(v is True for v in q3.values()), sum(v is None for v in q3.values())
        verdict = ("not estimable" if len(q3) - n_na < 4 else
                   "separates" if n3 >= 4 else "not separated")
        lines += [f"- memoryless floor (lowest CI bound of random / nociceptive reflex): {floor:+.2f} °C",
                  "", f"**Q3 verdict:** {n3}/{len(q3)} pass, {n_na} not estimable → {verdict}.", ""]

    # ---------------------------------------------------------------- Q4
    lines += ["## Q4: survival (descriptive)", ""]
    lines += [f"- {a}: survived {cell(l30.get((a, 'survived_frac')))}, "
              f"damage taken {cell(l30.get((a, 'damage_taken')))}" for a in learned]
    lines += ["", "## Figures", "", "![markers](markers.png)", "![trade-off by energy](tradeoff_by_energy.png)",
              "![trajectories, trade-off](trajectories_tradeoff.png)",
              "![trajectories, foraging](trajectories_foraging.png)", ""]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
