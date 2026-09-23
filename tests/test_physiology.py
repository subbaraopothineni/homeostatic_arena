"""Tests for the heat field, nociceptor, body state and drive."""
import math

import pytest

from arena.physiology import (
    AMBIENT_C,
    BodyState,
    HeatSource,
    ambient_temperature,
    homeostatic_drive,
    nociceptor_rate,
)


def test_ambient_far_from_sources_and_peak_at_source():
    sources = [HeatSource((0.0, 0.0), peak_c=60.0, sigma=0.6),
               HeatSource((3.0, 0.0), (3.0, 2.0), peak_c=55.0, sigma=0.4)]
    assert ambient_temperature((50.0, 50.0), sources) == pytest.approx(AMBIENT_C, abs=1e-9)
    assert ambient_temperature((0.0, 0.0), sources) == pytest.approx(60.0)
    assert ambient_temperature((3.0, 1.0), sources) == pytest.approx(55.0)
    assert ambient_temperature((1.0, 1.0), []) == AMBIENT_C


def test_ambient_uses_max_not_sum():
    a = HeatSource((0.0, 0.0), peak_c=60.0, sigma=1.0)
    b = HeatSource((0.0, 0.0), peak_c=60.0, sigma=1.0)
    assert ambient_temperature((0.0, 0.0), [a, b]) == pytest.approx(60.0)


def test_segment_distance():
    wall = HeatSource((0.0, -1.0), (0.0, 1.0))
    assert wall.distance((0.5, 0.0)) == pytest.approx(0.5)      # beside the middle
    assert wall.distance((-2.0, 0.3)) == pytest.approx(2.0)     # beside, off-centre
    assert wall.distance((0.0, 3.0)) == pytest.approx(2.0)      # beyond the p1 end
    assert wall.distance((0.0, -1.5)) == pytest.approx(0.5)     # beyond the p0 end
    assert wall.distance((3.0, 5.0)) == pytest.approx(5.0)      # diagonal from p1
    point = HeatSource((1.0, 1.0))
    assert point.distance((4.0, 5.0)) == pytest.approx(5.0)


def test_nociceptor_curve():
    assert nociceptor_rate(38.0) < 0.01
    assert nociceptor_rate(45.0) == pytest.approx(0.5)
    assert nociceptor_rate(52.0) > 0.99
    assert nociceptor_rate(-1e6) == 0.0 and nociceptor_rate(1e6) == 1.0


def _hold_skin(temp_c: float, seconds: float, dt: float = 0.001) -> BodyState:
    body = BodyState(skin_c=temp_c)
    for _ in range(int(round(seconds / dt))):
        body.step(dt, ambient_c=temp_c, effort_sq=0.0, on_charger=False)
    return body


def test_damage_at_60c_for_one_second():
    body = _hold_skin(60.0, 1.0)
    assert body.skin_c == pytest.approx(60.0)
    assert body.damage == pytest.approx(15.0 * 0.06, rel=1e-3)
    assert body.damage_taken == pytest.approx(body.damage)


def test_no_damage_at_40c():
    assert _hold_skin(40.0, 1.0).damage == 0.0


def test_skin_approaches_ambient_with_time_constant():
    body = BodyState(skin_c=AMBIENT_C)
    dt = 0.001
    for _ in range(int(0.3 / dt)):   # one time constant
        body.step(dt, ambient_c=AMBIENT_C + 10.0, effort_sq=0.0, on_charger=False)
    assert body.skin_c - AMBIENT_C == pytest.approx(10.0 * (1 - math.exp(-1)), rel=0.01)


def test_healing_below_onset():
    body = BodyState(damage=0.5)
    for _ in range(100):
        body.step(0.1, ambient_c=AMBIENT_C, effort_sq=0.0, on_charger=False)
    assert body.damage == pytest.approx(0.5 - 0.002 * 10.0)


def test_idle_energy_drain_and_charger():
    body = BodyState()
    for _ in range(200):
        body.step(0.05, ambient_c=AMBIENT_C, effort_sq=0.0, on_charger=False)
    assert body.energy == pytest.approx(1.0 - 0.12)

    body = BodyState(energy=0.5)
    for _ in range(20):
        body.step(0.05, ambient_c=AMBIENT_C, effort_sq=0.0, on_charger=True)
    assert body.energy == pytest.approx(0.5 + (0.25 - 0.012) * 1.0)


def test_motor_drain_and_death():
    body = BodyState(energy=0.01)
    body.step(1.0, ambient_c=AMBIENT_C, effort_sq=2.0, on_charger=False)
    assert body.energy == 0.0 and body.dead
    assert BodyState(damage=1.0).dead
    assert not BodyState().dead


def test_drive():
    assert homeostatic_drive(1.0, 0.0) == 0.0
    assert homeostatic_drive(0.5, 0.0) > homeostatic_drive(0.8, 0.0) > 0.0
    assert homeostatic_drive(1.0, 0.5) > homeostatic_drive(1.0, 0.2) > 0.0
    assert homeostatic_drive(0.0, 1.0) == pytest.approx(math.sqrt(3.0))
    # Damage is weighted twice as heavily as the same energy deficit.
    assert homeostatic_drive(1.0, 0.3) > homeostatic_drive(0.7, 0.0)
