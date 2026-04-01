import numpy as np
import pandas as pd
from unittest.mock import MagicMock

from aurora_siger.pipeline.validator import Validator, RULES
from aurora_siger.pipeline.launch import (
    ai_anomaly_check,
    calculate_autonomy,
    launch_decision,
)


# --- Validator tests ---

GOOD_READING = {
    "internal_temp": 22.3,
    "external_temp": 12.0,
    "structural_integrity": 1,
    "energy": 98.0,
    "vibration": 0.32,
    "tank_pressure": 305.0,
    "critical_modules": 1,
}

BAD_READING = {
    "internal_temp": 35.0,
    "external_temp": 130.0,
    "structural_integrity": 0,
    "energy": 40.0,
    "vibration": 0.8,
    "tank_pressure": 350.0,
    "critical_modules": 0,
}


def test_rules_has_all_columns():
    expected = {
        "internal_temp", "external_temp", "structural_integrity",
        "energy", "vibration", "tank_pressure", "critical_modules",
    }
    assert set(RULES.keys()) == expected


def test_validate_good_reading():
    validator = Validator()
    assert validator.validate_item(GOOD_READING) is True


def test_validate_bad_reading():
    validator = Validator()
    assert validator.validate_item(BAD_READING) is False


def test_validate_detail_good():
    validator = Validator()
    detail = validator.validate_item_detail(GOOD_READING)
    assert all(v == "OK" for v in detail.values())


def test_validate_detail_bad_has_failures():
    validator = Validator()
    detail = validator.validate_item_detail(BAD_READING)
    failed = [k for k, v in detail.items() if v != "OK"]
    assert len(failed) >= 1


def test_validate_boundary_energy_at_60():
    reading = {**GOOD_READING, "energy": 60.0}
    validator = Validator()
    assert validator.validate_item(reading) is True


def test_validate_boundary_energy_below_60():
    reading = {**GOOD_READING, "energy": 59.9}
    validator = Validator()
    assert validator.validate_item(reading) is False


# --- Energy analysis tests ---

def test_calculate_autonomy_default():
    autonomy = calculate_autonomy()
    assert autonomy is not None
    assert autonomy > 0


def test_calculate_autonomy_low_charge():
    autonomy = calculate_autonomy(charge_pct=50)
    assert autonomy is None


def test_calculate_autonomy_known_values():
    autonomy = calculate_autonomy(
        capacity_kwh=18,
        charge_pct=100,
        loss_pct=14,
        launch_power_kw=2,
        launch_time_min=9,
        orbital_power_kw=1.2,
        min_launch_charge=95,
    )
    expected_available = 18 * 1.0 * 0.86  # 15.48
    expected_launch = 2 * (9 / 60)  # 0.3
    expected_autonomy = (expected_available - expected_launch) / 1.2
    assert abs(autonomy - expected_autonomy) < 0.01


# --- AI anomaly check tests ---

def test_ai_anomaly_check_normal():
    mock_model = MagicMock()
    mock_model.anomaly_score.return_value = np.array([0.3])
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0.0] * 7])
    result = ai_anomaly_check(GOOD_READING, mock_model, mock_scaler, threshold=0.5)
    assert result is True


def test_ai_anomaly_check_anomaly():
    mock_model = MagicMock()
    mock_model.anomaly_score.return_value = np.array([0.8])
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0.0] * 7])
    result = ai_anomaly_check(BAD_READING, mock_model, mock_scaler, threshold=0.5)
    assert result is False
