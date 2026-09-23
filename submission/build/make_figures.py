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
from experiments.sensitivity_v02 import plot_sensitivity  # noqa: E402

OUT = ROOT / "submission" / "02_figures"
EMBED = ROOT / "submission" / "build" / "embed"
OUT.mkdir(parents=True, exist_ok=True)
EMBED.mkdir(parents=True, exist_ok=True)

# Every savefig writes the journal files (.pdf vector, .png at 600 dpi) to 02_figures
# and a 300-dpi copy to build/embed for the Word manuscript (keeps the .docx small).
_orig_savefig = matplotlib.figure.Figure.savefig


def _savefig(self, fname, *args, **kwargs):
    kwargs.pop("dpi", None)
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


def figure2_markers(path: Path) -> None:
    rows = list(csv.DictReader((ROOT / "results" / "summary.csv").open()))
    summary: dict[str, dict[str, Metric]] = {}
    for r in rows:
        summary.setdefault(r["agent"], {})[r["metric"]] = Metric(
            float(r["mean"]), float(r["ci_low"]), float(r["ci_high"]), int(r["n"]))
    plots.plot_markers(summary, path, 0.08, 0.9)


def figure5_sensitivity(path: Path) -> None:
    rows = list(csv.DictReader((ROOT / "results" / "v02" / "sensitivity.csv").open()))
    actual = [r for r in csv.DictReader((ROOT / "results" / "v02" / "hypotheses.csv").open())
              if r["variant"] == "FULL" and r["effect"] == "H1_spont_minus_self"]
    plot_sensitivity(rows, max(float(r["ci_high"]) for r in actual), path)


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
    figure5_sensitivity(OUT / "Figure5.png")
    plots_v02.plot_probes(v02["probes"], OUT / "Figure6.png")
    figure7_learners(OUT / "Figure7.png")
    for f in sorted(OUT.iterdir()):
        print(f"{f.name:28s} {f.stat().st_size / 1e6:6.2f} MB")


if __name__ == "__main__":
    main()
