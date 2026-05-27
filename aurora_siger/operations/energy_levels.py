"""Energy level as an output label (Fase 3 consolidation, §3.5).

Re-casts the team `main` branch's CRITICAL→SURPLUS state machine
(colonia_aurora/energy/energy_manager.py::_determine_level). Instead of
*controlling* modules, the level is now a read-only summary computed from
battery % and the OLS trend (slope + predicted next delta). The flow is
one-way: physics → level → presentation/decision.
"""

from aurora_siger.operations.constants import (
    LEVEL_CRITICAL_PCT, LEVEL_LOW_PCT, LEVEL_SURPLUS_PCT,
    SLOPE_CRITICAL, SLOPE_LOW,
)


def energy_level(battery_pct: float, slope: float, predicted_delta: float) -> str:
    """Returns one of CRITICAL/LOW/NOMINAL/HIGH/SURPLUS.

    Base level comes from battery %; a positive predicted delta lifts the
    mid-range to HIGH. A steeply negative OLS slope then collapses
    NOMINAL/HIGH/SURPLUS to LOW (anticipating a sharp drop before the battery
    actually falls); a mildly negative slope collapses HIGH/SURPLUS to NOMINAL.
    CRITICAL and LOW are never downgraded further by the slope rules.
    """
    if battery_pct < LEVEL_CRITICAL_PCT:
        base = "CRITICAL"
    elif battery_pct < LEVEL_LOW_PCT:
        base = "LOW"
    elif battery_pct > LEVEL_SURPLUS_PCT:
        base = "SURPLUS"
    elif predicted_delta > 0:
        base = "HIGH"
    else:
        base = "NOMINAL"

    if slope <= SLOPE_CRITICAL:
        if base in ("NOMINAL", "HIGH", "SURPLUS"):
            return "LOW"
        if base == "LOW":
            return "CRITICAL"
    elif slope <= SLOPE_LOW:
        if base in ("HIGH", "SURPLUS"):
            return "NOMINAL"
        if base == "NOMINAL":
            return "LOW"

    return base
