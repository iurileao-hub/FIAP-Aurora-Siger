import numpy as np
import pandas as pd
from aurora_siger.data.generation import generate_telemetry_dataset


def test_dataset_shape_default():
    df = generate_telemetry_dataset()
    assert df.shape == (100_000, 8)


def test_dataset_columns():
    df = generate_telemetry_dataset(n_samples=1000)
    expected_cols = [
        "internal_temp", "external_temp", "structural_integrity",
        "energy", "vibration", "tank_pressure", "critical_modules", "anomaly",
    ]
    assert list(df.columns) == expected_cols


def test_anomaly_ratio():
    df = generate_telemetry_dataset(n_samples=10_000, anomaly_ratio=0.03, seed=42)
    n_anomalies = df["anomaly"].sum()
    assert n_anomalies == int(10_000 * 0.03)


def test_anomaly_label_values():
    df = generate_telemetry_dataset(n_samples=1000)
    assert set(df["anomaly"].unique()) == {0, 1}


def test_energy_clipped():
    df = generate_telemetry_dataset(n_samples=50_000, seed=42)
    assert df["energy"].min() >= 0
    assert df["energy"].max() <= 100


def test_reproducibility():
    df1 = generate_telemetry_dataset(n_samples=1000, seed=42)
    df2 = generate_telemetry_dataset(n_samples=1000, seed=42)
    pd.testing.assert_frame_equal(df1, df2)
