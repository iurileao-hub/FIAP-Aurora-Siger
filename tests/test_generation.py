"""Tests for synthetic telemetry dataset generation.

Validates the shape, columns, anomaly distribution, value constraints,
and reproducibility of the generated dataset.
"""

import pandas as pd
from aurora_siger.data.generation import generate_telemetry_dataset


def test_dataset_shape():
    df = generate_telemetry_dataset(n_samples=100)
    # 7 telemetry columns + 1 anomaly label = 8
    assert df.shape == (100, 8)


def test_dataset_columns():
    df = generate_telemetry_dataset(n_samples=1000)
    expected_cols = [
        "internal_temp", "external_temp", "structural_integrity",
        "energy", "vibration", "tank_pressure", "critical_modules", "anomaly",
    ]
    assert list(df.columns) == expected_cols


def test_anomaly_ratio():
    # The number of anomalies must be exactly n_samples * anomaly_ratio (deterministic split)
    df = generate_telemetry_dataset(n_samples=10_000, anomaly_ratio=0.03, seed=42)
    n_anomalies = df["anomaly"].sum()
    assert n_anomalies == int(10_000 * 0.03)


def test_anomaly_label_values():
    df = generate_telemetry_dataset(n_samples=1000)
    assert set(df["anomaly"].unique()) == {0, 1}


def test_energy_clipped():
    # Energy is clipped to [0, 100] via np.clip in the generator
    df = generate_telemetry_dataset(n_samples=1_000, seed=42)
    assert df["energy"].min() >= 0
    assert df["energy"].max() <= 100


def test_reproducibility():
    # Same seed must produce identical datasets (uses np.random.RandomState, not global seed)
    df1 = generate_telemetry_dataset(n_samples=1000, seed=42)
    df2 = generate_telemetry_dataset(n_samples=1000, seed=42)
    pd.testing.assert_frame_equal(df1, df2)
