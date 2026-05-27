"""Tests for energy_levels.py (Fase 3 consolidation, §3.5)."""

from aurora_siger.operations.energy_levels import energy_level


# slope=0, predicted_delta chosen so the base branch is exercised cleanly.
def test_base_levels_from_battery_pct():
    assert energy_level(10.0, slope=0.0, predicted_delta=0.0) == "CRITICAL"
    assert energy_level(30.0, slope=0.0, predicted_delta=0.0) == "LOW"
    assert energy_level(95.0, slope=0.0, predicted_delta=0.0) == "SURPLUS"
    assert energy_level(60.0, slope=0.0, predicted_delta=5.0) == "HIGH"      # rising
    assert energy_level(60.0, slope=0.0, predicted_delta=-5.0) == "NOMINAL"  # falling


def test_steep_negative_slope_downgrades_one_step():
    # NOMINAL/HIGH/SURPLUS collapse to LOW under a steep drop
    assert energy_level(60.0, slope=-3.0, predicted_delta=5.0) == "LOW"
    # LOW collapses to CRITICAL
    assert energy_level(30.0, slope=-3.0, predicted_delta=0.0) == "CRITICAL"


def test_mild_negative_slope_softer_downgrade():
    # HIGH/SURPLUS → NOMINAL
    assert energy_level(95.0, slope=-1.0, predicted_delta=0.0) == "NOMINAL"
    # NOMINAL → LOW
    assert energy_level(60.0, slope=-1.0, predicted_delta=-5.0) == "LOW"


def test_critical_battery_unaffected_by_slope():
    # already CRITICAL; slope cannot make it worse
    assert energy_level(5.0, slope=-10.0, predicted_delta=-5.0) == "CRITICAL"
