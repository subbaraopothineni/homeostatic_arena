"""Sanity checks on the world layouts."""
import math

import pytest

from arena.physiology import AMBIENT_C, ambient_temperature
from arena.scenarios import SCENARIOS, foraging, tradeoff


def test_lookup():
    assert SCENARIOS["foraging"]().name == "foraging"
    assert SCENARIOS["tradeoff"](0.3).start_energy == 0.3


@pytest.mark.parametrize("y", [4.2, -4.2])
def test_tradeoff_gaps_are_safe(y):
    s = tradeoff()
    assert ambient_temperature((0.0, y), s.heat_sources) < 35.0


def test_tradeoff_wall_is_hot_and_start_and_charger_are_cool():
    s = tradeoff()
    assert ambient_temperature((0.0, 0.0), s.heat_sources) == pytest.approx(
        s.heat_sources[0].peak_c)
    assert ambient_temperature(s.start_xy, s.heat_sources) < AMBIENT_C + 0.5
    assert ambient_temperature(s.charger_xy, s.heat_sources) < AMBIENT_C + 0.5


def test_foraging_layout_inside_arena_and_charger_cool():
    s = foraging()
    for src in s.heat_sources:
        assert max(abs(c) for c in src.p0) < s.half_size
    assert ambient_temperature(s.charger_xy, s.heat_sources) < 30.0
    assert ambient_temperature(s.start_xy, s.heat_sources) < 30.0
    assert math.dist(s.start_xy, s.charger_xy) > 2.0
