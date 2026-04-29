"""Mathematical models of the Mars landing phenomena.

Four elementary functions that approximate physical quantities relevant to the
descent. Kept side-effect-free and dependency-free so they can be plotted from
notebooks, the CLI, or the figure-generation script alike.
"""

import math


def descent_altitude(
    t: float,
    h0: float = 2000.0,
    v0: float = 80.0,
    a: float = 3.7,
) -> float:
    """Altitude during the free-fall phase of descent (before retro-rockets).

    Formula: ``h(t) = h0 - v0*t - 0.5 * a * t**2``.

    Args:
        t: Seconds since the start of descent.
        h0: Initial altitude in meters (default 2000).
        v0: Initial vertical velocity in m/s (default 80).
        a: Mars surface gravity in m/s² (default 3.7).

    Returns:
        Altitude in meters, clamped at 0 to model ground impact.
    """
    return max(0.0, h0 - v0 * t - 0.5 * a * t**2)


def fuel_consumption(v: float, c0: float = 10.0, k: float = 0.02) -> float:
    """Fuel consumption rate as a function of braking velocity.

    Formula: ``C(v) = c0 * exp(k * v)``. Models the empirical observation that
    aggressive braking burns exponentially more fuel than gradual deceleration.

    Args:
        v: Braking velocity in m/s.
        c0: Baseline consumption rate in kg/s.
        k: Exponential growth coefficient.

    Returns:
        Fuel consumption rate in kg/s.
    """
    return c0 * math.exp(k * v)


def solar_energy(
    t: float,
    a_coeff: float = 15.0,
    t_mid: float = 12.3,
    e_max: float = 2200.0,
) -> float:
    """Solar power generation throughout a Martian day.

    Formula: ``E(t) = -a_coeff * (t - t_mid)**2 + e_max``. Inverted parabola
    peaking at solar noon and dropping to zero at sunrise/sunset.

    Args:
        t: Hour of the Martian day (0 to ~24.6).
        a_coeff: Parabola opening coefficient.
        t_mid: Hour of solar peak.
        e_max: Peak generation in watts.

    Returns:
        Power generation in watts, clamped at 0.
    """
    return max(0.0, -a_coeff * (t - t_mid) ** 2 + e_max)


def surface_temperature(
    t: float,
    t_avg: float = -60.0,
    amplitude: float = 40.0,
    period: float = 24.62,
    phase: float = 0.0,
) -> float:
    """Surface temperature variation across one Martian sol.

    Formula: ``T(t) = t_avg + amplitude * sin(2*pi*t / period - phase)``. A sol
    lasts about 24 h 37 min; baseline -60 °C with 40 °C amplitude.

    Args:
        t: Hour of the Martian day (0 to ~24.6).
        t_avg: Daily mean temperature in °C.
        amplitude: Variation amplitude in °C.
        period: Sol duration in hours.
        phase: Phase shift in radians.

    Returns:
        Surface temperature in °C.
    """
    return t_avg + amplitude * math.sin(2 * math.pi * t / period - phase)
