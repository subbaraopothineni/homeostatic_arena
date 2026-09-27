"""Build the manuscript figures (vector PDF + 600-dpi PNG + 300-dpi PNG for the Word file).

Every figure is redrawn from the committed result tables, except Figure 7, which
replays the first five (deterministic) foraging episodes of each Study 1b agent.
Run from the repository root:

    python submission/build/make_figures.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.figure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from arena.agency import agency  # noqa: E402
from arena.scenarios import Scenario, foraging, tradeoff  # noqa: E402
from experiments import plots, plots_v02  # noqa: E402
from experiments.markers import Metric, run_foraging  # noqa: E402
from experiments.plots import INK, INK_2, SURFACE, _heat_field  # noqa: E402
from experiments.run_baseline import learned_factories  # noqa: E402
from experiments.run_v02 import load_tables  # noqa: E402

OUT = ROOT / "submission" / "02_figures"
EMBED = ROOT / "submission" / "build" / "embed"
OUT.mkdir(parents=True, exist_ok=True)
EMBED.mkdir(parents=True, exist_ok=True)

# Every savefig writes the journal files (.pdf vector, .png at 600 dpi) to 02_figures
# and a 300-dpi copy to build/embed for the Word manuscript (keeps the .docx small).
_orig_savefig = matplotlib.figure.Figure.savefig


def _savefig(self, fname, *args, **kwargs):
    kwargs.pop("dpi", None)
    if getattr(self, "_suptitle", None) is not None:   # journal style: the caption carries the title
        self._suptitle.remove()
        self._suptitle = None
    base = Path(fname).with_suffix("")
    _orig_savefig(self, f"{base}.pdf", **kwargs)
    _orig_savefig(self, f"{base}.png", dpi=600, **kwargs)
    _orig_savefig(self, EMBED / f"{base.name}.png", dpi=300, **kwargs)


matplotlib.figure.Figure.savefig = _savefig


def figure1_worlds(path: Path) -> None:
    """The three worlds, and the geometry of the self/other test."""
    lamp_world = agency()
    shown = Scenario(**{**lamp_world.__dict__,
                        "heat_sources": lamp_world.heat_sources + [lamp_world.extra["lamp"]]})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.9), layout="constrained")
    for ax, scen, title in ((axes[0], foraging(), "(a) Foraging world (Study 1)"),
                            (axes[1], tradeoff(0.9), "(b) Trade-off world (Study 1)"),
                            (axes[2], shown, "(c) Agency world, lamp on (Study 2)")):
        im = _heat_field(ax, scen, 0.6)
        ax.set_title(title, loc="left")
    ax = axes[1]
    ax.plot(-3, 0, "o", ms=7, mfc=SURFACE, mec=INK, mew=1.4)
    ax.annotate("start", (-3, 0), xytext=(0, -14), textcoords="offset points", ha="center",
                fontsize=8, color=INK)
    ax.annotate("", (2.4, 0), (-2.8, 0), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    ax.annotate("short route:\nthrough the wall", (0.25, -0.35), va="top", fontsize=8, color=INK)
    ax.annotate("", (2.6, 0.5), (-2.8, 0.25), arrowprops=dict(
        arrowstyle="->", color=INK_2, lw=1.2, ls="--", connectionstyle="arc3,rad=-0.9"))
    ax.annotate("long route: around", (-1.6, 4.3), fontsize=8, color=INK_2)
    ax = axes[2]
    ax.add_patch(Circle((0, 0), 0.5, fill=False, edgecolor=INK, lw=1.5, ls="--"))
    ax.annotate("switch pad", (0, -0.55), xytext=(0, -6), textcoords="offset points",
                ha="center", va="top", fontsize=8, color=INK)
    ax.annotate("lamp", (3, 3), xytext=(0, -26), textcoords="offset points", ha="center",
                fontsize=8, color=SURFACE, fontweight="bold")
    for (x, y), label, color in (((-1.0, 0.0), "SELF trial:\nagent → pad", plots_v02.COLORS["FULL"]),
                                 ((1.0, 0.0), "OTHER trial:\nother robot → pad",
                                  plots_v02.COLORS["REFLEX"])):
        ax.add_patch(Circle((x, y), 0.25, color=color, zorder=3))
        tx = -0.45 if x > 0 else 0.45
        ax.add_patch(FancyArrowPatch((x, y), (x + tx, y), arrowstyle="->", mutation_scale=12,
                                     color=color, lw=1.6, zorder=3))
        ax.annotate(label, (x, y), xytext=(-2 if x < 0 else 2, 12), textcoords="offset points",
                    ha="right" if x < 0 else "left", va="bottom", fontsize=8, color=INK)
    fig.colorbar(im, ax=axes, shrink=0.8, label="ambient temperature (°C)")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def _summary(*files: Path) -> dict[str, dict[str, Metric]]:
    out: dict[str, dict[str, Metric]] = {}
    for f in files:
        for r in csv.DictReader(f.open()):
            out.setdefault(r["agent"], {})[r["metric"]] = Metric(
                float(r["mean"]), float(r["ci_low"]), float(r["ci_high"]), int(r["n"]))
    return out


def figure2_markers(path: Path) -> None:
    """Five memoryless or one-bit agents; sensitization from the 100-seed runs (as in the text)."""
    res = ROOT / "results"
    summary = _summary(res / "summary.csv", res / "minimal_controls" / "summary.csv")
    seeds100 = _summary(res / "seeds100" / "summary.csv", res / "minimal_controls" / "seeds100" / "summary.csv")
    for agent in summary:
        m = seeds100[agent]["sensitization_c"]
        # One qualifying episode gives no interval: shown as not estimable, as in the text.
        summary[agent]["sensitization_c"] = m if m.n >= 2 else Metric(float("nan"), float("nan"),
                                                                      float("nan"), m.n)
    plots.plot_markers(summary, path, 0.08, 0.9)


PRECISION_COLORS = {"exact": "#0b3c75", "edge error 0.05 m": "#2a78d6",
                    "edge error 0.1 m": "#6ea4e8", "edge error 0.2 m": "#a3c4ee"}
PRECISION_LABELS = {"exact": "exact timing", "edge error 0.05 m": "edge error σ 0.05 m (≈0.6 steps)",
                    "edge error 0.1 m": "σ 0.1 m (≈1.3 steps)", "edge error 0.2 m": "σ 0.2 m (≈2.5 steps)"}


def figure6_sensitivity(path: Path) -> None:
    """Effect size and passing runs against the blend weight, per self-model precision."""
    v02 = ROOT / "results" / "v02"
    actual = [r for r in csv.DictReader((v02 / "hypotheses.csv").open())
              if r["variant"] == "FULL" and r["effect"] == "H1_spont_minus_self"]
    upper = max(float(r["ci_high"]) for r in actual)
    base = [r for r in csv.DictReader((v02 / "sensitivity.csv").open())
            if float(r["w"]) == 0 and r["hypothesis"] == "H1_spont_minus_self"]
    w0_effect = np.mean([float(r["mean"]) for r in base])
    rows = [r for r in csv.DictReader((v02 / "sensitivity_noisy.csv").open())
            if r["hypothesis"] == "H1_spont_minus_self"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), layout="constrained")
    markers = dict(zip(PRECISION_COLORS, ("o", "s", "^", "D")))
    for level, color in PRECISION_COLORS.items():
        sel = [r for r in rows if r["level"] == level]
        ws = sorted({float(r["w"]) for r in sel})
        eff = [np.mean([float(r["mean"]) for r in sel if float(r["w"]) == w]) for w in ws]
        runs = [sum(r["counts"] == "True" for r in sel if float(r["w"]) == w) for w in ws]
        kw = dict(color=color, marker=markers[level], ms=6, lw=2, mec="white", mew=1)
        axes[0].plot([0.0] + ws, [w0_effect] + eff, label=PRECISION_LABELS[level], **kw)
        axes[1].plot([0.0] + ws, [0] + runs, label=PRECISION_LABELS[level], **kw)
    axes[0].axhline(upper, color=INK_2, lw=1)
    axes[0].annotate(f"largest upper CI bound\nof the real agents (+{upper:.3f})", xy=(0.006, upper),
                     xytext=(0.0, 0.45), fontsize=8, color=INK_2,
                     arrowprops=dict(arrowstyle="->", color=INK_2, lw=0.8))
    axes[0].set_ylabel("H1 effect, mean of 5 runs\nrelPE(SPONT) − relPE(SELF)")
    axes[0].set_title("(a) Effect size", loc="left")
    axes[1].axhline(4, color=INK_2, lw=1)
    axes[1].annotate("pass rule: 4 of 5", (0.0, 4), xytext=(4, 5), textcoords="offset points",
                     fontsize=8, color=INK_2)
    axes[1].set_ylim(-0.2, 5.2)
    axes[1].set_ylabel("runs meeting H1 (of 5)")
    axes[1].set_title("(b) Runs meeting the pre-registered rule", loc="left")
    for ax in axes:
        ax.set_xscale("symlog", linthresh=0.02)
        ax.set_xticks([0, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0], ["0", "0.02", "0.05", "0.1", "0.25", "0.5", "1"])
        ax.set_xlabel("blend weight w (share of the self-model mixed in)")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=4, fontsize=8, frameon=False,
               title="precision of the self-model", title_fontsize=8)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def figure7_learners(path: Path) -> None:
    factories = learned_factories(ROOT / "results" / "study1b" / "models")
    logs = {name: run_foraging(f, 5, agent_name=name) for name, f in factories.items()}
    plots.plot_trajectories_foraging(logs, foraging(), path, n_show=5)


def main() -> None:
    v02 = load_tables(ROOT / "results" / "v02")
    figure1_worlds(OUT / "Figure1.png")
    figure2_markers(OUT / "Figure2.png")
    plots_v02.plot_relpe(v02["relpe"], OUT / "Figure3.png")
    plots_v02.plot_hypotheses(v02["hypotheses"], OUT / "Figure4.png")
    plots_v02.plot_probes(v02["probes"], OUT / "Figure5.png")
    figure6_sensitivity(OUT / "Figure6.png")
    figure7_learners(OUT / "Figure7.png")
    for f in sorted(OUT.iterdir()):
        print(f"{f.name:28s} {f.stat().st_size / 1e6:6.2f} MB")


if __name__ == "__main__":
    main()
