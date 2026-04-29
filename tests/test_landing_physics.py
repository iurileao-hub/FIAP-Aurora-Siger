"""Tests for the four physics functions of the MGPEB.

Each function is verified by closed-form properties (initial values, peaks,
clamping, monotonicity) rather than golden-file values, so the tests survive
parameter tuning.
"""

import math

import pytest

from aurora_siger.landing.physics import (
    descent_altitude,
    fuel_consumption,
    solar_energy,
    surface_temperature,
)


# --- descent_altitude(t) = max(0, h0 - v0*t - 0.5*a*t**2) ---

def test_descent_altitude_at_t0_equals_h0():
    assert descent_altitude(0) == 2000.0


def test_descent_altitude_clamps_at_zero():
    assert descent_altitude(1000) == 0.0


def test_descent_altitude_is_monotonic_decreasing():
    values = [descent_altitude(t) for t in range(0, 25)]
    assert all(a >= b for a, b in zip(values, values[1:]))


def test_descent_altitude_respects_custom_parameters():
    # h0=100, v0=10, a=2 → h(2) = 100 - 20 - 4 = 76
    assert descent_altitude(2, h0=100, v0=10, a=2) == pytest.approx(76.0)


# --- fuel_consumption(v) = c0 * exp(k*v) ---

def test_fuel_consumption_at_v0_equals_c0():
    assert fuel_consumption(0) == pytest.approx(10.0)


def test_fuel_consumption_is_monotonic_increasing():
    values = [fuel_consumption(v) for v in range(0, 200, 20)]
    assert all(a < b for a, b in zip(values, values[1:]))


def test_fuel_consumption_grows_exponentially():
    # Doubling v should more than double C(v) when k*v is large enough.
    c50 = fuel_consumption(50)
    c100 = fuel_consumption(100)
    assert c100 > 2 * c50


# --- solar_energy(t) = max(0, -a*(t - t_mid)**2 + e_max) ---

def test_solar_energy_peaks_at_t_mid():
    peak = solar_energy(12.3)
    assert peak == pytest.approx(2200.0)


def test_solar_energy_is_clamped_at_zero():
    # Far from solar noon the parabola goes negative — must clamp at 0.
    # Threshold: |t - 12.3| > sqrt(2200/15) ≈ 12.11 → t < 0.19 or t > 24.41.
    assert solar_energy(0) == 0.0
    assert solar_energy(25) == 0.0
    assert solar_energy(30) == 0.0


def test_solar_energy_is_symmetric_around_noon():
    morning = solar_energy(10)
    afternoon = solar_energy(14.6)  # same distance from t_mid=12.3
    assert morning == pytest.approx(afternoon)


# --- surface_temperature(t) = t_avg + amplitude * sin(2*pi*t/period - phase) ---

def test_surface_temperature_equals_average_at_t0():
    # sin(0) = 0 → temperature equals t_avg
    assert surface_temperature(0) == pytest.approx(-60.0)


def test_surface_temperature_within_amplitude_band():
    for t in range(0, 25):
        temp = surface_temperature(t)
        assert -100.0 <= temp <= -20.0


def test_surface_temperature_is_periodic():
    # Period defaults to 24.62 — same value should repeat one period later.
    assert surface_temperature(5) == pytest.approx(surface_temperature(5 + 24.62))
