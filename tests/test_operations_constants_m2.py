"""Test M2 constants for energy levels, trends, and failure modes."""

from aurora_siger.operations import constants as c


def test_energy_levels_ordered_low_to_high():
    assert c.ENERGY_LEVELS == ("CRITICAL", "LOW", "NOMINAL", "HIGH", "SURPLUS")


def test_battery_level_thresholds_are_ascending_percentages():
    assert 0 < c.LEVEL_CRITICAL_PCT < c.LEVEL_LOW_PCT < c.LEVEL_SURPLUS_PCT < 100


def test_slope_thresholds_are_negative_and_ordered():
    assert c.SLOPE_CRITICAL < c.SLOPE_LOW < 0


def test_trend_window_positive():
    assert c.TREND_WINDOW > 1


def test_failure_constants_present():
    assert 0.0 < c.FAILURE_PROB_PER_HOUR < 1.0
    lo, hi = c.REPAIR_DURATION_HOURS
    assert 0 < lo <= hi


def test_history_keys_extended_with_m2_outputs():
    for key in ("energy_level", "slope", "predicted_delta", "broken_count"):
        assert key in c.HISTORY_KEYS
    # no duplicates introduced
    assert len(c.HISTORY_KEYS) == len(set(c.HISTORY_KEYS))
