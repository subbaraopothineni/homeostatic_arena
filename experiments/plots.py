"""Figures for the baseline run (matplotlib, static PNG).

Agent colours follow the entity in every figure (categorical slots 1-3 of a
colour-vision-deficiency-validated palette). The heat field uses a single-hue
sequential ramp; trajectories are drawn in ink so they stay legible on it.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

from arena.physiology import PhysiologyParams, ambient_temperature  # noqa: E402
from arena.scenarios import Scenario  # noqa: E402
from experiments.markers import (  # noqa: E402
    HARMFUL_NOCICEPTOR, EpisodeLog, Metric, find_encounters)

AGENT_COLORS = {
    "random": "#2a78d6",
    "reflex_nociceptive": "#eb6834",
    "reflex_thermotactic": "#1baf7a",
    # Literal-withdrawal variants (run separately; validated as their own pair).
    "reflex_nociceptive_literal": "#e87ba4",
    "reflex_thermotactic_literal": "#4a3aa7",
}
AGENT_LABELS = {
    "random": "Random",
    "reflex_nociceptive": "Reflex\n(nociceptive)",
    "reflex_thermotactic": "Reflex\n(thermotactic)",
    "reflex_nociceptive_literal": "Literal reflex\n(nociceptive)",
    "reflex_thermotactic_literal": "Literal reflex\n(thermotactic)",
}
LEARNED_COLOR = "#4a3aa7"     # Study 1b learning agents (all seeds share the entity colour)
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a8983"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"


def color_of(agent: str) -> str:
    if agent.startswith("learned"):
        return LEARNED_COLOR
    return AGENT_COLORS.get(agent, "#52514e")


def label_of(agent: str) -> str:
    if agent.startswith("learned_seed"):
        return "Learned\n(seed " + agent.split("seed")[1] + ")"
    return AGENT_LABELS.get(agent, agent)


# Single-hue (orange) sequential ramp for temperature, near-white at 25 C.
HEAT_CMAP = LinearSegmentedColormap.from_list(
    "heat", ["#fbf6f2", "#f9d9c8", "#f3ad8a", "#eb6834", "#b8431a", "#7a2a0e"])

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": INK_3,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titlesize": 11,
    "axes.labelsize": 9.5,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 9.5,
    "legend.frameon": False,
    "legend.fontsize": 8.5,
})


def _heat_field(ax, scenario: Scenario, charger_radius: float, n: int = 220):
    h = scenario.half_size
    xs = np.linspace(-h, h, n)
    field = np.array([[ambient_temperature((x, y), scenario.heat_sources) for x in xs]
                      for y in xs])
    im = ax.imshow(field, extent=(-h, h, -h, h), origin="lower", cmap=HEAT_CMAP,
                   vmin=25.0, vmax=60.0, interpolation="bilinear")
    ax.add_patch(Rectangle((-h, -h), 2 * h, 2 * h, fill=False, edgecolor=INK_2, lw=2.0))
    cx, cy = scenario.charger_xy
    ax.add_patch(Circle((cx, cy), charger_radius, fill=False, edgecolor=INK, lw=1.5))
    ax.annotate("charger", (cx, cy + charger_radius), xytext=(0, 3),
                textcoords="offset points", ha="center", va="bottom", fontsize=8, color=INK,
                bbox=dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none", alpha=0.85))
    ax.set_xlim(-h - 0.2, h + 0.2)
    ax.set_ylim(-h - 0.2, h + 0.2)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xticks([-5, 0, 5])
    ax.set_yticks([-5, 0, 5])
    return im


def _trajectories(ax, logs: Sequence[EpisodeLog]):
    for log in logs:
        x, y = log.data["x"], log.data["y"]
        ax.plot(x, y, color=INK, lw=1.0, alpha=0.75, solid_capstyle="round")
        ax.plot(x[0], y[0], "o", ms=5, mfc=SURFACE, mec=INK, mew=1.2)
        if log.died:
            ax.plot(x[-1], y[-1], "x", ms=8, color=INK, mew=2.0)


def _trajectory_legend(fig):
    handles = [
        plt.Line2D([], [], color=INK, lw=1.0, label="trajectory"),
        plt.Line2D([], [], ls="", marker="o", ms=5, mfc=SURFACE, mec=INK, label="start"),
        plt.Line2D([], [], ls="", marker="x", ms=8, color=INK, mew=2.0, label="death"),
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=3)


def plot_trajectories_foraging(logs_by_agent: dict[str, list[EpisodeLog]], scenario: Scenario,
                               path: Path, n_show: int = 5,
                               params: PhysiologyParams | None = None) -> None:
    params = params or PhysiologyParams()
    agents = list(logs_by_agent)
    fig, axes = plt.subplots(1, len(agents), figsize=(4.0 * len(agents) + 1.0, 4.9),
                             layout="constrained")
    im = None
    for ax, agent in zip(np.atleast_1d(axes), agents):
        im = _heat_field(ax, scenario, params.charger_radius)
        _trajectories(ax, logs_by_agent[agent][:n_show])
        ax.set_title(label_of(agent).replace("\n", " "))
    fig.colorbar(im, ax=axes, shrink=0.8, label="ambient temperature (°C)")
    fig.suptitle(f"Foraging world: first {n_show} episodes per agent (90 s)",
                 color=INK, fontsize=12)
    _trajectory_legend(fig)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def plot_trajectories_tradeoff(logs_by_agent: dict[str, list[EpisodeLog]],
                               scenarios: dict[float, Scenario], path: Path,
                               n_show: int = 5, params: PhysiologyParams | None = None) -> None:
    params = params or PhysiologyParams()
    agents = list(logs_by_agent)
    energies = sorted(scenarios)
    fig, axes = plt.subplots(len(energies), len(agents),
                             figsize=(4.0 * len(agents) + 1.0, 4.3 * len(energies) + 0.8),
                             squeeze=False, layout="constrained")
    im = None
    for i, e in enumerate(energies):
        for j, agent in enumerate(agents):
            ax = axes[i, j]
            im = _heat_field(ax, scenarios[e], params.charger_radius)
            logs = [lg for lg in logs_by_agent[agent] if lg.start_energy == e][:n_show]
            _trajectories(ax, logs)
            label = label_of(agent).replace("\n", " ")
            ax.set_title(f"{label}\nstart energy {e}")
    fig.colorbar(im, ax=axes, shrink=0.6, label="ambient temperature (°C)")
    fig.suptitle(f"Trade-off world: first {n_show} episodes per condition (60 s)",
                 color=INK, fontsize=12)
    _trajectory_legend(fig)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def _bar_panel(ax, agents: Sequence[str], metrics: Sequence[Metric], title: str,
               ylabel: str, fmt: str, zero_line: bool = False, ylim=None) -> None:
    xs = np.arange(len(agents))
    for x, agent, m in zip(xs, agents, metrics):
        if math.isnan(m.mean):
            ax.text(x, 0, "n/a", ha="center", va="bottom", color=INK_2, fontsize=8.5)
            continue
        ax.bar(x, m.mean, width=0.55, color=color_of(agent), zorder=2)
        if not (math.isnan(m.ci_low) or math.isnan(m.ci_high)):
            ax.errorbar(x, m.mean, yerr=[[m.mean - m.ci_low], [m.ci_high - m.mean]],
                        fmt="none", ecolor=INK, elinewidth=1.2, capsize=4, zorder=3)
            top = max(m.ci_high, m.mean)
        else:
            top = m.mean
        bottom = min(m.ci_low if not math.isnan(m.ci_low) else m.mean, m.mean)
        y_text, va = (top, "bottom") if m.mean >= 0 else (bottom, "top")
        ax.annotate(f"{fmt.format(m.mean)}\n(n={m.n})", (x, y_text),
                    xytext=(0, 3 if va == "bottom" else -3), textcoords="offset points",
                    ha="center", va=va, fontsize=8, color=INK_2)
    if zero_line:
        ax.axhline(0.0, color=INK_2, lw=1.0, zorder=1)
    ax.set_xticks(xs, [label_of(a) for a in agents])
    ax.set_title(title, loc="left")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    if ylim is not None:
        ax.set_ylim(*ylim)
    else:
        lo, hi = ax.get_ylim()
        pad = 0.18 * (hi - lo)
        ax.set_ylim(lo - (pad if lo < 0 else 0), hi + pad)


def plot_markers(summary: dict[str, dict[str, Metric]], path: Path, e_low: float,
                 e_high: float) -> None:
    """2 x 2 bar charts with 95% CIs: survival, anticipation, trade-off, sensitization."""
    agents = list(summary)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.4))
    _bar_panel(axes[0, 0], agents, [summary[a]["survived_frac"] for a in agents],
               "1. Survival (foraging, 90 s)", "fraction of episodes survived", "{:.2f}",
               ylim=(0, 1.15))
    _bar_panel(axes[0, 1], agents, [summary[a]["anticipation_rate"] for a in agents],
               "2. Anticipatory avoidance", "encounters left before nociceptor > 0.5",
               "{:.2f}", ylim=(0, 1.15))
    _bar_panel(axes[1, 0], agents, [summary[a]["tradeoff_score"] for a in agents],
               "3. Motivational trade-off",
               f"crossing rate at E={e_low} minus at E={e_high}", "{:+.2f}", zero_line=True)
    _bar_panel(axes[1, 1], agents, [summary[a]["sensitization_c"] for a in agents],
               "4. Sensitization", "peak °C per encounter, after − before first harm",
               "{:+.2f}", zero_line=True)
    fig.suptitle("Sentience-marker baseline (bars: mean; whiskers: 95% CI)",
                 color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def plot_tradeoff_by_energy(summary: dict[str, dict[str, Metric]],
                            energies: Sequence[float], path: Path) -> None:
    """Crossing and entry rates against start energy, one line per agent."""
    agents = list(summary)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    panels = [("crossing_rate", "Full crossings through the wall"),
              ("entry_rate", "Entries into the wall core"),
              ("reached_charger", "Reached the charger")]
    for ax, (key, title) in zip(axes, panels):
        for agent in agents:
            ms = [summary[agent][f"{key}@{e}"] for e in energies]
            y = np.array([m.mean for m in ms])
            lo = np.array([m.ci_low for m in ms])
            hi = np.array([m.ci_high for m in ms])
            ax.fill_between(energies, lo, hi, color=color_of(agent), alpha=0.12, lw=0)
            ax.plot(energies, y, color=color_of(agent), lw=2.0, marker="o", ms=6,
                    mec=SURFACE, mew=1.5, label=label_of(agent).replace("\n", " "))
        ax.set_title(title, loc="left")
        ax.set_xlabel("start energy")
        ax.set_xticks(list(energies))
        ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("fraction of episodes (95% CI band)")
    axes[-1].legend(loc="upper right")
    fig.suptitle("Trade-off world by start energy", color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def plot_physiology_trace(log: EpisodeLog, path: Path,
                          params: PhysiologyParams | None = None) -> None:
    """Skin temperature, nociceptor, energy and damage over one episode."""
    params = params or PhysiologyParams()
    d = log.data
    t = d["t"]
    encounters = find_encounters(d["ambient_c"], d["nociceptor"])
    color = color_of(log.agent)
    fig, axes = plt.subplots(4, 1, figsize=(10, 8.5), sharex=True)

    def shade(ax):
        for e in encounters:
            t1 = t[min(e.end, len(t) - 1)]
            ax.axvspan(t[e.start], t1, color="#f3ad8a" if e.harmful else GRID,
                       alpha=0.45 if e.harmful else 0.7, lw=0, zorder=0)

    ax = axes[0]
    shade(ax)
    ax.plot(t, d["ambient_c"], color=INK_3, lw=1.2, label="ambient")
    ax.plot(t, d["skin_c"], color=color, lw=2.0, label="skin")
    ax.axhline(params.damage_onset_c, color=INK_2, lw=1.0,
               label=f"damage onset ({params.damage_onset_c:.0f} °C)")
    ax.set_ylabel("temperature (°C)")
    ax.set_ylim(top=max(62.0, float(d["ambient_c"].max()) + 2))
    ax.legend(loc="upper right", ncol=3)

    ax = axes[1]
    shade(ax)
    ax.plot(t, d["nociceptor"], color=color, lw=2.0)
    ax.axhline(HARMFUL_NOCICEPTOR, color=INK_2, lw=1.0,
               label=f"harmful-encounter threshold ({HARMFUL_NOCICEPTOR})")
    ax.legend(loc="upper right")
    ax.set_ylabel("nociceptor")
    ax.set_ylim(-0.03, 1.05)

    ax = axes[2]
    shade(ax)
    ax.plot(t, d["energy"], color=color, lw=2.0)
    on = d["on_charger"].astype(bool)
    if on.any():
        ax.plot(t[on], d["energy"][on], ls="", marker="o", ms=3, color=INK, label="on charger")
        ax.legend(loc="lower left")
    ax.set_ylabel("energy")
    ax.set_ylim(-0.03, 1.05)

    ax = axes[3]
    shade(ax)
    ax.plot(t, d["damage"], color=color, lw=2.0)
    ax.set_ylabel("damage")
    ax.set_ylim(-0.03, max(0.2, float(d["damage"].max()) * 1.2))
    ax.set_xlabel("time (s)")

    outcome = "died" if log.died else "survived"
    n_harm = sum(e.harmful for e in encounters)
    fig.suptitle(f"Physiology trace: {label_of(log.agent).replace(chr(10), ' ')}, "
                 f"{log.scenario} seed {log.seed} ({outcome}; {len(encounters)} heat encounters, "
                 f"{n_harm} harmful; grey = encounter, orange = harmful)",
                 color=INK, fontsize=10.5)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
