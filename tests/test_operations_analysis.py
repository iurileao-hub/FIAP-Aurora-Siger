"""Tests for aurora_siger.operations.analysis — energy balance analysis."""

import pytest

from aurora_siger.operations.analysis import (
    analyze_balance,
    summarize_history,
    aggregate_by_sol,
    status_distribution,
    generation_breakdown,
    critical_moments,
    write_log,
)

# A tiny 3-hour history covering one risk hour, one surplus hour, one balanced.
HISTORY = {
    "total_generation_kw": [50.0, 200.0, 105.0],
    "total_consumption_kw": [100.0, 100.0, 100.0],
    "solar_generation_kw": [10.0, 120.0, 60.0],
    "wind_generation_kw": [20.0, 50.0, 30.0],
    "nuclear_generation_kw": [20.0, 30.0, 15.0],
    "storm": ["clear", "moderate", "clear"],
    "battery_charge_kwh": [300.0, 350.0, 340.0],
    "alerts": [["x"], [], []],
}


def test_analyze_balance_classifies_three_regimes():
    """Risk when gen < con; surplus when gen > 1.1*con; balanced otherwise."""
    assert analyze_balance(50.0, 100.0)["status"] == "risk"
    assert analyze_balance(200.0, 100.0)["status"] == "surplus"
    assert analyze_balance(105.0, 100.0)["status"] == "balanced"


def test_summarize_history_counts_storm_and_alert_hours():
    """Aggregates metrics: total_steps, storm_hours, alert_hours, max/min gen."""
    s = summarize_history(HISTORY)
    assert s["total_steps"] == 3
    assert s["storm_hours"] == 1
    assert s["alert_hours"] == 1
    assert s["max_generation_kw"] == 200.0


def test_aggregate_by_sol_single_partial_sol():
    """Aggregates into per-sol rows; 3 hours = 1 partial sol."""
    rows = aggregate_by_sol(HISTORY)
    assert len(rows) == 1
    assert rows[0]["sol"] == 0 and rows[0]["hours"] == 3


def test_status_distribution_sums_to_total():
    """Distribution of risk/balanced/surplus counts sums to 3."""
    counts = status_distribution(HISTORY)
    assert counts["risk"] == 1 and counts["surplus"] == 1 and counts["balanced"] == 1


def test_generation_breakdown_shares_sum_to_one():
    """Solar + wind + nuclear shares must sum to 1.0."""
    bd = generation_breakdown(HISTORY)
    total_share = bd["solar"]["share"] + bd["wind"]["share"] + bd["nuclear"]["share"]
    assert abs(total_share - 1.0) < 1e-9


def test_critical_moments_finds_worst_and_best():
    """Identifies hour with biggest deficit and biggest surplus."""
    cm = critical_moments(HISTORY)
    assert cm["worst_deficit"]["delta_kw"] == -50.0  # hour 0: 50 - 100
    assert cm["biggest_surplus"]["delta_kw"] == 100.0  # hour 1: 200 - 100


def test_write_log_creates_file(tmp_path):
    """Writes history to log file with header and per-step lines."""
    path = tmp_path / "logs" / "run.txt"
    write_log(HISTORY, str(path), seed=42)
    content = path.read_text(encoding="utf-8")
    assert "Aurora Siger" in content and "seed=42" in content
