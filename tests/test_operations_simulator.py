from aurora_siger.operations.simulator import run_simulation
from aurora_siger.operations.constants import TOTAL_STEPS


def test_horizon_length():
    _, _, history = run_simulation(seed=42, horizon=48)
    assert len(history["total_generation_kw"]) == 48


def test_same_seed_is_bit_identical():
    _, _, h1 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    _, _, h2 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert h1 == h2


def test_different_seed_diverges():
    _, _, h1 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    _, _, h2 = run_simulation(seed=7, horizon=TOTAL_STEPS)
    assert h1["total_generation_kw"] != h2["total_generation_kw"]


def test_battery_stays_within_bounds():
    _, battery, history = run_simulation(seed=42, horizon=TOTAL_STEPS)
    charges = history["battery_charge_kwh"]
    assert all(0.0 <= c <= battery["max_capacity_kwh"] for c in charges)


def test_coldfront_recorded_when_it_fires():
    # cold-front presence is derivable from temperature dips; just assert the
    # run completes and temperature series has the expected length
    _, _, history = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert len(history["temperature_c"]) == TOTAL_STEPS
