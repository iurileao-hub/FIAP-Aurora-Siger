"""Launch decision pipeline — AI check, energy analysis, and final GO/NO-GO."""

import numpy as np

from aurora_siger.pipeline.validator import Validator, RULES


FEATURE_COLUMNS = list(RULES.keys())


def ai_anomaly_check(
    reading: dict[str, float | int],
    model: object,
    scaler: object,
    threshold: float,
) -> bool:
    """Run AI anomaly detection on a single telemetry reading.

    Returns True if the reading is considered normal (score below threshold).
    """
    features = np.array([[reading[col] for col in FEATURE_COLUMNS]])
    X_scaled = scaler.transform(features)
    score = model.anomaly_score(X_scaled)[0]

    print(f"\n=== IA ANOMALY CHECK ===")
    print(f"Anomaly Score: {score:.4f}")

    if score >= threshold:
        print("IA detectou anomalia")
        return False

    print("IA nao detectou anomalias")
    return True


def calculate_autonomy(
    capacity_kwh: float = 18,
    charge_pct: float = 100,
    loss_pct: float = 14,
    launch_power_kw: float = 2,
    launch_time_min: float = 9,
    orbital_power_kw: float = 1.2,
    min_launch_charge: float = 95,
) -> float | None:
    """Calculate orbital autonomy in hours after launch.

    Returns None if charge is below minimum required for launch.
    """
    print("\n=== ANALISE ENERGETICA ===")

    if charge_pct < min_launch_charge:
        print("Carga insuficiente para lancamento")
        return None

    available_energy = capacity_kwh * (charge_pct / 100) * (1 - loss_pct / 100)
    launch_energy = launch_power_kw * (launch_time_min / 60)
    autonomy = (available_energy - launch_energy) / orbital_power_kw

    print(f"Energia disponivel: {available_energy:.2f} kWh")
    print(f"Consumo no lancamento: {launch_energy:.2f} kWh")
    print(f"Autonomia orbital: {autonomy:.2f} h")

    return autonomy


def launch_decision(
    reading: dict[str, float | int],
    model: object,
    scaler: object,
    threshold: float,
) -> bool:
    """Run the full 3-stage GO/NO-GO pipeline.

    Stages:
        1. Telemetry validation (safe ranges)
        2. AI anomaly detection (Isolation Forest score)
        3. Energy analysis (orbital autonomy)

    Returns True if all stages pass (GO), False otherwise (NO-GO).
    """
    print("\n=================================")
    print("AURORA SIGER — DECISAO DE LANCAMENTO")
    print("=================================")

    # Stage 1: Telemetry
    validator = Validator()

    print("\n=== TELEMETRIA ===")
    details = validator.validate_item_detail(reading)
    telemetry_ok = all(v == "OK" for v in details.values())
    for k, v in details.items():
        print(f"{k}: {v}")

    # Stage 2: AI
    ai_ok = ai_anomaly_check(reading, model, scaler, threshold)

    # Stage 3: Energy
    autonomy = calculate_autonomy(charge_pct=reading["energy"])

    # Final decision
    go = telemetry_ok and ai_ok and autonomy is not None
    if go:
        print("\n >>> PRONTO PARA DECOLAR <<<")
    else:
        print("\n >>> DECOLAGEM ABORTADA <<<")

    return go
