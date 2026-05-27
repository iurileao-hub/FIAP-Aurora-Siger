"""Realistic climate model for the Aurora Siger colony (Fase 3).

Ported from the team's `iuri` branch. Two changes from the original:
  * randomness is injected (a RandomLCG instance) instead of using stdlib
    `random`, so the whole simulation is deterministic per seed and two
    runs can proceed independently;
  * a ColdFrontState FSM is added (Fase 3 event) to stress the thermal model.
"""

import math

from aurora_siger.operations.constants import (
    V_BASE, V_AMPLITUDE, SEASONAL_FACTOR, V_NOISE_SIGMA,
    T_MEAN, A_DAILY, A_SEASONAL, PHI_DAILY, T_NOISE_SIGMA,
    SOLS_PER_MARS_YEAR,
    BASE_PROB_PER_SOL, DURATION_HOURS, WIND_BONUS_THRESHOLD, PERIHELION_FACTOR,
    DIDACTIC_EVENT_SOL, DIDACTIC_EVENT_HOUR,
    TAU_BASE, TAU_WIND_FACTOR, TAU_WIND_THRESHOLD,
    PANEL_LOSS_PER_SOL, CLEANING_RECOVERY, PANEL_FACTOR_FLOOR,
    COLDFRONT_PROB_PER_SOL, COLDFRONT_DURATION_HOURS, COLDFRONT_DELTA_C,
)


def compute_tau(storm, wind):
    """Atmospheric opacity = base per class + wind bonus."""
    extra = TAU_WIND_FACTOR * max(0.0, wind - TAU_WIND_THRESHOLD)
    return TAU_BASE[storm] + extra


def solar_transmission(tau):
    """Beer-Lambert: transmission = exp(-tau) (zenith simplification)."""
    return math.exp(-tau)


def update_panel_factor(current_factor, cleaning_drawn, rng):
    """Continuous deposition and (if cleaning_drawn) dust-devil recovery."""
    new = max(PANEL_FACTOR_FLOOR, current_factor - PANEL_LOSS_PER_SOL)
    if cleaning_drawn:
        recovery = rng.uniform(*CLEANING_RECOVERY)
        new = min(1.0, new + recovery)
    return new


def sample_wind(hour, rng):
    """Wind speed in m/s for the given local hour (0..23)."""
    daily_component = V_AMPLITUDE * max(0.0, math.sin(math.pi * (hour - 6) / 12))
    noise = rng.gauss(0, V_NOISE_SIGMA)
    return max(0.0, (V_BASE + daily_component) * SEASONAL_FACTOR + noise)


def sample_temperature(sol, hour, rng):
    """Temperature in °C for the given sol and hour (before cold-front offset)."""
    daily = A_DAILY * math.sin(2 * math.pi * (hour - PHI_DAILY) / 24)
    seasonal = A_SEASONAL * math.sin(2 * math.pi * sol / SOLS_PER_MARS_YEAR)
    noise = rng.gauss(0, T_NOISE_SIGMA)
    return T_MEAN + daily + seasonal + noise


class StormState:
    """Dust-storm FSM: 'clear' → 'light'/'moderate'/'severe', with persistence."""

    def __init__(self):
        self.state = "clear"
        self.hours_remaining = 0

    def _start_probability(self, klass, wind_max_24h):
        prob = BASE_PROB_PER_SOL[klass]
        wind_bonus = max(0.0, (wind_max_24h - WIND_BONUS_THRESHOLD) / 10.0)
        return prob * (1 + wind_bonus) * PERIHELION_FACTOR

    def advance(self, wind_max_24h, sol, hour, rng, force_event=False):
        """Advances one hour of the FSM."""
        if (force_event and sol == DIDACTIC_EVENT_SOL and hour == DIDACTIC_EVENT_HOUR
                and self.state == "clear"):
            self.state = "moderate"
            min_h, max_h = DURATION_HOURS["moderate"]
            self.hours_remaining = rng.randint(min_h, max_h)
            return

        if self.state != "clear":
            self.hours_remaining -= 1
            if self.hours_remaining <= 0:
                self.state = "clear"
                self.hours_remaining = 0
            return

        for klass in ("severe", "moderate", "light"):  # rarest first
            hour_prob = self._start_probability(klass, wind_max_24h) / 24.0
            if rng.random() < hour_prob:
                self.state = klass
                min_h, max_h = DURATION_HOURS[klass]
                self.hours_remaining = rng.randint(min_h, max_h)
                return


class ColdFrontState:
    """Cold-front FSM: applies COLDFRONT_DELTA_C to temperature while active."""

    def __init__(self):
        self.active = False
        self.hours_remaining = 0

    def advance(self, sol, hour, rng):
        """Advances one hour: tick down if active, else roll a new front."""
        if self.active:
            self.hours_remaining -= 1
            if self.hours_remaining <= 0:
                self.active = False
                self.hours_remaining = 0
            return
        if rng.random() < COLDFRONT_PROB_PER_SOL / 24.0:
            self.active = True
            lo, hi = COLDFRONT_DURATION_HOURS
            self.hours_remaining = rng.randint(lo, hi)

    def temperature_offset(self):
        return COLDFRONT_DELTA_C if self.active else 0.0
