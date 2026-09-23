"""Functional analogues of thermal sensing, tissue damage and energy balance.

Everything here is a *functional analogue* of biology: a thermal field, a skin
temperature with thermal inertia, a nociceptor signal, a damage variable, an
energy store and a homeostatic drive. No claim is made that any agent using
these variables has subjective experience.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

# Room temperature of the arena (deg C).
AMBIENT_C = 25.0

# Heat-nociceptor half-activation temperature (deg C). Human heat-pain
# threshold is ~43-45 deg C; the TRPV1 channel activates at ~43 deg C
# (Caterina et al., 1997, Nature 389:816).
NOCICEPTOR_THRESHOLD_C = 45.0

# Width of the nociceptor's sigmoid (deg C). Chosen so the signal goes from
# ~0 to ~1 over a few degrees, like the steep heat-response curves of
# polymodal C-fibre nociceptors.
NOCICEPTOR_SLOPE_C = 1.0

XY = Sequence[float]


# --------------------------------------------------------------------------
# Heat field
# --------------------------------------------------------------------------

@dataclass
class HeatSource:
    """A Gaussian heat source: a point (p1 is None) or a line segment ("heat wall").

    Temperature rise falls off with the distance to the point or to the nearest
    point on the segment.
    """

    p0: tuple[float, float]
    p1: tuple[float, float] | None = None
    peak_c: float = 60.0
    sigma: float = 0.6  # m

    def distance(self, xy: XY) -> float:
        """Distance (m) from `xy` to the source point or nearest point on the segment."""
        px, py = float(xy[0]), float(xy[1])
        ax, ay = self.p0
        if self.p1 is None:
            return math.hypot(px - ax, py - ay)
        bx, by = self.p1
        abx, aby = bx - ax, by - ay
        length_sq = abx * abx + aby * aby
        if length_sq == 0.0:
            return math.hypot(px - ax, py - ay)
        t = ((px - ax) * abx + (py - ay) * aby) / length_sq
        t = min(1.0, max(0.0, t))
        return math.hypot(px - (ax + t * abx), py - (ay + t * aby))

    def nearest_point(self, xy: XY) -> tuple[float, float]:
        """The point of the source (the point itself, or on the segment) closest to `xy`."""
        if self.p1 is None:
            return self.p0
        px, py = float(xy[0]), float(xy[1])
        (ax, ay), (bx, by) = self.p0, self.p1
        abx, aby = bx - ax, by - ay
        length_sq = abx * abx + aby * aby
        if length_sq == 0.0:
            return self.p0
        t = min(1.0, max(0.0, ((px - ax) * abx + (py - ay) * aby) / length_sq))
        return ax + t * abx, ay + t * aby

    def temperature_rise(self, xy: XY) -> float:
        """Rise above ambient (deg C) at `xy`: (peak - ambient) * exp(-d^2 / 2 sigma^2)."""
        d = self.distance(xy)
        return (self.peak_c - AMBIENT_C) * math.exp(-d * d / (2.0 * self.sigma ** 2))


def ambient_temperature(xy: XY, sources: Sequence[HeatSource]) -> float:
    """Air/radiant temperature at `xy`: ambient plus the largest single rise.

    The max (not the sum) keeps two nearby sources from exceeding either peak.
    """
    rise = max((s.temperature_rise(xy) for s in sources), default=0.0)
    return AMBIENT_C + rise


# --------------------------------------------------------------------------
# Sensors and drive
# --------------------------------------------------------------------------

def nociceptor_rate(skin_c: float) -> float:
    """Normalised heat-nociceptor firing rate in [0, 1] (logistic in skin temperature)."""
    z = (skin_c - NOCICEPTOR_THRESHOLD_C) / NOCICEPTOR_SLOPE_C
    # Guard against overflow for very cold/hot inputs.
    if z < -60.0:
        return 0.0
    if z > 60.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def homeostatic_drive(energy: float, damage: float,
                      w_energy: float = 1.0, w_damage: float = 2.0) -> float:
    """Distance of the internal state from its setpoints (energy = 1, damage = 0).

    Drive-reduction reward (Keramati & Gutkin, 2014, eLife) is the decrease of
    this quantity from one step to the next.
    """
    return math.sqrt(w_energy * (1.0 - energy) ** 2 + w_damage * damage ** 2)


# --------------------------------------------------------------------------
# Body state
# --------------------------------------------------------------------------

@dataclass
class PhysiologyParams:
    """Rates and thresholds of the body model (units: deg C, seconds, metres)."""

    skin_tau_s: float = 0.3          # skin thermal time constant (s)
    damage_onset_c: float = 45.0     # damage begins above this skin temperature
    damage_rate: float = 0.06        # damage per deg C above onset per second
    heal_rate: float = 0.002         # repair per second when below onset
    energy_base_drain: float = 0.012  # per second, idle metabolism
    energy_motor_drain: float = 0.010  # per second x sum(action^2)
    charge_rate: float = 0.25        # per second on the charger
    charger_radius: float = 0.6      # m


@dataclass
class BodyState:
    """Skin temperature, energy store and damage variable of one agent."""

    skin_c: float = AMBIENT_C
    energy: float = 1.0
    damage: float = 0.0
    params: PhysiologyParams = field(default_factory=PhysiologyParams)
    # Cumulative damage inflicted (not reduced by healing); for logging only.
    damage_taken: float = 0.0

    def step(self, dt: float, ambient_c: float, effort_sq: float, on_charger: bool) -> None:
        """Advance the body by `dt` seconds (explicit Euler)."""
        p = self.params
        self.skin_c += (ambient_c - self.skin_c) * dt / p.skin_tau_s

        if self.skin_c > p.damage_onset_c:
            new_damage = self.damage + p.damage_rate * (self.skin_c - p.damage_onset_c) * dt
        else:
            new_damage = self.damage - p.heal_rate * dt
        new_damage = min(1.0, max(0.0, new_damage))
        self.damage_taken += max(0.0, new_damage - self.damage)
        self.damage = new_damage

        self.energy -= (p.energy_base_drain + p.energy_motor_drain * effort_sq) * dt
        if on_charger:
            self.energy += p.charge_rate * dt
        self.energy = min(1.0, max(0.0, self.energy))

    @property
    def dead(self) -> bool:
        """True once energy is exhausted or damage is total."""
        return self.energy <= 0.0 or self.damage >= 1.0
