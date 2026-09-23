"""Figures for the v0.2 self/world and self/other experiments."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from experiments.plots import GRID, INK, INK_2, INK_3, SURFACE  # noqa: E402  (also sets rcParams)

COLORS = {
    "FULL": "#2a78d6", "UNTRAINED": "#eb6834", "COMPARATOR": "#1baf7a", "NO-CHANGE": INK_3,
    "RAW-INPUT": INK_3, "NOEFF": "#eda100", "NOFWD": "#e87ba4", "REFLEX": "#4a3aa7",
}
HYP_TITLES = {
    "H1_spont_minus_self": "H1 self-prediction\nrelPE(SPONT) − relPE(SELF)",
    "H2_omit_minus_noevent": "H2 omission surprise\nabsPE(SELF-OMIT) − absPE(NOEVENT)",
    "H3a_selfblind_interaction": "H3a self-blind hurts SELF\nmore than OTHER",
    "H3b_otherblind_interaction": "H3b other-blind hurts OTHER\nmore than SELF",
}
CONDS = ("SELF", "OTHER", "SPONT", "OTHER-ONPAD", "SPONT-ONPAD")


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def _symlog(ax, axis: str, linthresh: float) -> None:
    """Symmetric log scale with clean decade ticks (0, +-0.1, +-1, ...) and plain labels."""
    getattr(ax, f"set_{axis}scale")("symlog", linthresh=linthresh)
    lo, hi = getattr(ax, f"get_{axis}lim")()
    ticks = [0.0]
    k = math.ceil(math.log10(linthresh))
    while 10.0 ** k <= max(abs(lo), abs(hi)) * 1.0001:
        ticks += [t for t in (10.0 ** k, -(10.0 ** k)) if lo <= t <= hi]
        k += 1
    getattr(ax, f"set_{axis}ticks")(sorted(ticks), [f"{t:g}" for t in sorted(ticks)])
    getattr(ax, f"set_{axis}lim")(lo, hi)


def plot_training(models: Path, path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), layout="constrained")
    panels = [("mean_seconds", "survival time per episode (s)"),
              ("death_rate", "fraction of episodes ending in death"),
              ("fwd_ratio", "prediction error / no-change error")]
    seen = set()
    for log in sorted(models.glob("*_seed*.csv")):
        variant = log.stem.split("_seed")[0]
        rows = list(csv.DictReader(log.open()))
        steps = np.array([_f(r["steps"]) for r in rows]) / 1e6
        series = {
            "mean_seconds": [_f(r["mean_seconds"]) for r in rows],
            "death_rate": [_f(r["death_rate"]) for r in rows],
            "fwd_ratio": [_f(r["fwd_loss"]) / _f(r["no_change_mse"]) for r in rows],
        }
        for ax, (key, _) in zip(axes, panels):
            y = np.array(series[key], dtype=float)
            if np.all(np.isnan(y)):
                continue
            k = max(1, min(10, len(y)))                 # smooth over up to 10 updates
            y = np.convolve(np.nan_to_num(y, nan=np.nanmean(y)), np.ones(k) / k, mode="valid")
            ax.plot(steps[k - 1:], y, color=COLORS[variant], lw=1.4, alpha=0.85,
                    label=variant if variant not in seen else None)
        seen.add(variant)
    for ax, (key, label) in zip(axes, panels):
        ax.set_xlabel("environment steps (millions)")
        ax.set_title(label, loc="left")
    axes[2].axhline(1.0, color=INK_2, lw=1.0)
    axes[2].set_yscale("log")
    axes[0].legend(loc="lower right")
    fig.suptitle("Training (each line one run; 10-update moving average)", color=INK)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_hypotheses(rows: list[dict], path: Path) -> None:
    """Forest plot: every run's effect with its 95% CI; filled = counts for the verdict."""
    runs = list(dict.fromkeys(r["label"] for r in rows))
    runs = [r for r in runs if r != "NO-CHANGE"]
    fig, axes = plt.subplots(1, 4, figsize=(15, 0.32 * len(runs) + 1.8), sharey=True,
                             layout="constrained")
    for ax, (hyp, title) in zip(axes, HYP_TITLES.items()):
        for y, run in enumerate(runs):
            r = next((x for x in rows if x["label"] == run and x["effect"] == hyp), None)
            if r is None:
                continue
            m, lo, hi = _f(r["mean"]), _f(r["ci_low"]), _f(r["ci_high"])
            color = COLORS[r["variant"]]
            ax.plot([lo, hi], [y, y], color=color, lw=1.6)
            counted = str(r["counts_for_verdict"]) == "True"
            ax.plot(m, y, "o", ms=6, color=color, mfc=color if counted else SURFACE, mew=1.5)
        ax.axvline(0.0, color=INK_2, lw=1.0)
        _symlog(ax, "x", 0.01)
        ax.set_title(title, loc="left", fontsize=9.5)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(range(len(runs)), runs)
    axes[0].invert_yaxis()
    fig.suptitle("Pre-registered effects per run (95% bootstrap CI; positive = predicted "
                 "direction; filled = counts toward the verdict)", color=INK, fontsize=11)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_relpe(rows: list[dict], path: Path) -> None:
    groups = ("FULL", "UNTRAINED", "COMPARATOR", "NO-CHANGE")
    fig, axes = plt.subplots(1, len(groups), figsize=(14, 3.8), sharey=True, layout="constrained")
    x = np.arange(len(CONDS))
    for ax, g in zip(axes, groups):
        runs = sorted({r["label"] for r in rows if r["variant"] == g})
        for run in runs:
            ys = [next((_f(r["mean"]) for r in rows if r["label"] == run and r["condition"] == c),
                       math.nan) for c in CONDS]
            ax.plot(x, ys, "o-", color=COLORS[g], ms=5, lw=1.0, alpha=0.8)
        ax.axhline(1.0, color=INK_2, lw=1.0)
        ax.axhline(0.0, color=INK_3, lw=0.8)
        ax.set_xticks(x, [c.replace("-", "-\n") for c in CONDS], fontsize=8)
        ax.set_title(g + (f" ({len(runs)} runs)" if len(runs) > 1 else ""), loc="left")
    for ax in axes:
        _symlog(ax, "y", 0.1)
    axes[0].set_ylabel("relative prediction error at the lamp change\n"
                       "(0 = fully predicted, 1 = no change predicted)")
    fig.suptitle("How surprising is the same lamp change, by its cause?", color=INK)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_dissociation(rows: list[dict], path: Path) -> None:
    """Increase in relPE when self-motion or other-robot signals are frozen."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True, layout="constrained")
    for ax, abl in zip(axes, ("self-blind", "other-blind")):
        for g in ("FULL", "UNTRAINED", "COMPARATOR"):
            runs = sorted({r["label"] for r in rows if r["variant"] == g})
            for i, run in enumerate(runs):
                def val(c):
                    base = next((_f(r["mean"]) for r in rows if r["label"] == run
                                 and r["condition"] == c), math.nan)
                    abl_v = next((_f(r["mean"]) for r in rows if r["label"] == run
                                  and r["condition"] == f"{c}|{abl}"), math.nan)
                    return abl_v - base
                ax.plot([0, 1], [val("SELF"), val("OTHER")], "o-", color=COLORS[g], ms=6,
                        lw=1.2, alpha=0.85, label=g if i == 0 else None)
        ax.axhline(0.0, color=INK_2, lw=1.0)
        ax.set_xticks([0, 1], ["SELF-caused", "OTHER-caused"])
        ax.set_xlim(-0.3, 1.3)
        _symlog(ax, "y", 0.1)
        ax.set_title(f"{abl}: increase in relPE", loc="left")
    axes[0].set_ylabel("relPE(ablated) − relPE(intact)")
    axes[1].legend(loc="upper left")
    fig.suptitle("Double dissociation test (H3): which signals does each prediction use?",
                 color=INK)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_t1(t1_rows: list[dict], beh_rows: list[dict], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), layout="constrained")
    conds = ("WORLD", "BODY", "NONE")
    x = np.arange(len(conds))
    ax = axes[0]
    for offset, g in zip((-0.2, 0.0, 0.2), ("FULL", "UNTRAINED", "NO-CHANGE")):
        runs = sorted({r["label"] for r in t1_rows if r["variant"] == g})
        for i, run in enumerate(runs):
            ys = [np.nanmean([_f(r["intero_share"]) for r in t1_rows
                              if r["label"] == run and r["condition"] == c]) for c in conds]
            ax.plot(x + offset, ys, "o", color=COLORS[g], ms=6, label=g if i == 0 else None)
    ax.set_xticks(x, ["WORLD event\n(lamp far away)", "BODY event\n(metabolic shock)", "NONE"])
    ax.set_ylabel("share of prediction error on body channels")
    ax.set_title("Where does the surprise go?", loc="left")
    ax.legend(loc="center right")
    ax = axes[1]
    for offset, g in zip((-0.12, 0.12), ("FULL", "REFLEX")):
        runs = sorted({r["label"] for r in beh_rows if r["variant"] == g})
        for i, run in enumerate(runs):
            ys = [np.mean([_f(r["toward_charger_m"]) for r in beh_rows
                           if r["label"] == run and r["condition"] == c]) for c in conds]
            ax.plot(x + offset, ys, "o", color=COLORS[g], ms=6, label=g if i == 0 else None)
    ax.axhline(0.0, color=INK_2, lw=1.0)
    ax.set_xticks(x, ["WORLD", "BODY", "NONE"])
    ax.set_ylabel("movement toward the charger in 5 s (m)")
    ax.set_title("Behaviour after the event (start energy 0.65)", loc="left")
    ax.legend(loc="upper right")
    fig.suptitle("T1 body vs world (pre-registered as expected to be passed by trivial "
                 "controls)", color=INK)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_probes(rows: list[dict], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True, layout="constrained")
    for ax, probe, title in ((axes[0], "who", "Who caused the lamp change? (3 classes)"),
                             (axes[1], "what", "What happened: world / body / nothing?")):
        for g in ("FULL", "UNTRAINED", "RAW-INPUT"):
            runs = sorted({r["label"] for r in rows if r["variant"] == g})
            for i, run in enumerate(runs):
                pts = sorted((int(r["lag"]), _f(r["accuracy"])) for r in rows
                             if r["label"] == run and r["probe"] == probe)
                if pts:
                    lx, ly = zip(*pts)
                    ax.plot(lx, ly, "o-", color=COLORS[g], ms=5, lw=1.2, alpha=0.85,
                            label=g if i == 0 else None)
        ax.axhline(1 / 3, color=INK_2, lw=1.0)
        ax.set_xlabel("steps after the event (memory lag)")
        ax.set_title(title, loc="left")
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("cross-validated decoding accuracy\n(line: chance = 1/3)")
    axes[0].legend(loc="lower left")
    fig.suptitle("Exploratory probes (decodable ≠ used; compare with the raw-input baseline)",
                 color=INK)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def make_all(tables: dict[str, list[dict]], models: Path, out: Path) -> None:
    plot_training(models, out / "fig_training.png")
    plot_hypotheses(tables["hypotheses"], out / "fig_hypotheses.png")
    plot_relpe(tables["relpe"], out / "fig_relpe.png")
    plot_dissociation(tables["relpe"], out / "fig_dissociation.png")
    plot_t1(tables["t1_trials"], tables["t1_behaviour"], out / "fig_t1_body_world.png")
    plot_probes(tables["probes"], out / "fig_probes.png")
