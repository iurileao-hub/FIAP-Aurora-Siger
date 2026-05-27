"""Tests for aurora_siger.operations.state — initial state builder."""

from aurora_siger.operations.state import initial_state
from aurora_siger.operations.constants import HISTORY_KEYS, BATTERY_CAPACITY_KWH


def test_initial_state_shape():
    """Verify initial_state() returns a 3-tuple with correct shapes."""
    climate, battery, history = initial_state()
    assert climate["sol"] == 0 and climate["hour"] == 0
    assert battery["max_capacity_kwh"] == BATTERY_CAPACITY_KWH
    assert battery["emergency_reserve_kwh"] == BATTERY_CAPACITY_KWH * 0.20
    assert set(history) == set(HISTORY_KEYS)
    assert all(history[k] == [] for k in HISTORY_KEYS)
