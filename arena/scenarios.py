"""World layouts, stored as plain data so experiments can be reproduced exactly."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from arena.physiology import HeatSource


@dataclass
class Scenario:
    """A square arena [-half_size, half_size]^2 with heat sources and one charger."""

    name: str
    heat_sources: list[HeatSource]
    charger_xy: tuple[float, float]
    start_xy: tuple[float, float]
    start_energy: float = 1.0
    randomize_start: bool = False
    half_size: float = 5.0
    max_seconds: float = 90.0
    notes: str = ""
    extra: dict = field(default_factory=dict)


def foraging() -> Scenario:
    """General survival world: two hot spots and a charger far from the start.

    The agent must leave its start, find the charger by its beacon (chemical
    gradient analogue) and avoid the hot spots on the way.
    """
    return Scenario(
        name="foraging",
        heat_sources=[
            HeatSource((-1.5, 1.5), peak_c=60.0, sigma=0.7),
            HeatSource((2.0, -1.0), peak_c=60.0, sigma=0.7),
        ],
        charger_xy=(3.2, 3.2),
        start_xy=(-3.0, -3.0),
        randomize_start=True,
        notes="Two 60 C hot spots; charger in the NE corner; random safe start.",
    )


def tradeoff(start_energy: float = 0.9) -> Scenario:
    """Motivational trade-off world (after the hermit-crab shell/shock paradigm,
    Elwood & Appel, 2009, Animal Behaviour).

    A heat wall along x = 0 separates the start (west) from the charger (east).
    Short route: straight through the wall (costs damage).
    Long route: around the wall ends via the gaps at |y| > 4 (costs energy).

    Wall parameters were changed from the design brief's 58 C / sigma 0.35 m to
    60 C / sigma 0.5 m: with the original wall a run through it cost only 0.007
    damage at 2 m/s (0.04 at 1.6 m/s), so the "costly" short route was nearly
    free. See experiments.markers.tradeoff_design_check.
    """
    return Scenario(
        name="tradeoff",
        heat_sources=[HeatSource((0.0, -3.3), (0.0, 3.3), peak_c=60.0, sigma=0.5)],
        charger_xy=(3.0, 0.0),
        start_xy=(-3.0, 0.0),
        start_energy=start_energy,
        randomize_start=False,
        max_seconds=60.0,
        notes="Heat wall x=0, |y|<=3.3; detour gaps at |y|>4; charger east.",
        extra={"wall_half_length": 3.3, "gap_y": 4.2},
    )


SCENARIOS: dict[str, Callable[..., Scenario]] = {
    "foraging": foraging,
    "tradeoff": tradeoff,
}
