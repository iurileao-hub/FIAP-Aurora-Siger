"""Synthetic telemetry dataset generation for Aurora SIGER."""

import numpy as np
import pandas as pd


def generate_telemetry_dataset(
    n_samples: int = 100_000,
    anomaly_ratio: float = 0.03,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic spacecraft telemetry dataset.

    Args:
        n_samples: Total number of samples.
        anomaly_ratio: Fraction of anomalous samples (0-1).
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with 7 telemetry columns + 'anomaly' label.
    """
    rng = np.random.RandomState(seed)
    n_anomalies = int(n_samples * anomaly_ratio)
    n_normal = n_samples - n_anomalies

    # --- Normal data ---
    tank_pressure_normal = rng.normal(loc=305, scale=15, size=n_normal)
    # Logistic (sigmoid) function to model a realistic pressure-failure
    # correlation: failure probability rises smoothly as pressure increases.
    # 340 = inflection point (pressure where failure chance hits 50%)
    # 5   = steepness (lower = sharper transition from safe to dangerous)
    failure_prob = 1 / (1 + np.exp(-(tank_pressure_normal - 340) / 5))
    failure_prob = np.clip(failure_prob, 0, 1)

    df_normal = pd.DataFrame({
        "internal_temp": rng.normal(loc=22, scale=1.5, size=n_normal),
        "external_temp": rng.normal(loc=10, scale=8, size=n_normal),
        "structural_integrity": rng.binomial(1, 1 - failure_prob, size=n_normal),
        "energy": np.clip(rng.normal(loc=98, scale=2, size=n_normal), 0, 100),
        "vibration": rng.normal(loc=0.3, scale=0.1, size=n_normal),
        "tank_pressure": tank_pressure_normal,
        "critical_modules": rng.binomial(1, 1 - failure_prob, size=n_normal),
    })

    # --- Anomaly data (shifted distributions) ---
    tank_pressure_anomaly = rng.normal(loc=360, scale=25, size=n_anomalies)
    # Same sigmoid but inflection at 300 atm (vs 340 for normal data),
    # so anomalous readings have much higher failure probability at the
    # same pressure — reflecting degraded structural conditions.
    failure_prob_anomaly = 1 / (1 + np.exp(-(tank_pressure_anomaly - 300) / 5))
    failure_prob_anomaly = np.clip(failure_prob_anomaly, 0, 1)

    # Bimodal anomaly: half overheating (~35 °C), half overcooling (~5 °C).
    # Both fall outside the safe range [18, 26] but in opposite directions,
    # simulating two distinct failure modes.
    internal_temp_anomaly = np.concatenate([
        rng.normal(35, 3, size=n_anomalies // 2),
        rng.normal(5, 2, size=n_anomalies - n_anomalies // 2),
    ])
    rng.shuffle(internal_temp_anomaly)

    df_anomaly = pd.DataFrame({
        "internal_temp": internal_temp_anomaly,
        "external_temp": rng.normal(loc=60, scale=20, size=n_anomalies),
        "structural_integrity": rng.binomial(1, 1 - failure_prob_anomaly, size=n_anomalies),
        "energy": np.clip(rng.normal(loc=40, scale=15, size=n_anomalies), 0, 100),
        "vibration": rng.normal(loc=1.2, scale=0.4, size=n_anomalies),
        "tank_pressure": tank_pressure_anomaly,
        "critical_modules": rng.binomial(1, failure_prob_anomaly, size=n_anomalies),
    })

    # --- Combine and label ---
    df_normal["anomaly"] = 0
    df_anomaly["anomaly"] = 1

    return pd.concat([df_normal, df_anomaly], ignore_index=True)
