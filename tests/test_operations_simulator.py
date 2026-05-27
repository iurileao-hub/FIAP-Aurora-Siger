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


def test_temperature_series_has_full_horizon():
    _, _, history = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert len(history["temperature_c"]) == TOTAL_STEPS


def test_step_applies_active_coldfront_offset_to_temperature():
    """An active cold front shifts the recorded temperature by exactly
    COLDFRONT_DELTA_C — the only M1-new wiring inside step().

    We reproduce step()'s rng-consumption order (a wind draw, then a
    temperature draw) with a probe of the same seed. Because an *active*
    ColdFrontState.advance() draws no random numbers, the temperature recorded
    by step() must equal the un-shifted base sample plus the cold-front offset.
    """
    from collections import deque

    from aurora_siger.operations.simulator import step
    from aurora_siger.operations.climate import (
        StormState, ColdFrontState, sample_wind, sample_temperature,
    )
    from aurora_siger.operations.state import initial_state
    from aurora_siger.operations.hierarchies import build_criticality_tree
    from aurora_siger.operations.rng import RandomLCG
    from aurora_siger.operations.constants import COLDFRONT_DELTA_C

    probe = RandomLCG(123)
    sample_wind(0, probe)                       # mirror step(): wind is drawn first
    expected_base_temp = sample_temperature(0, 0, probe)

    climate, battery, history = initial_state()
    cold_front = ColdFrontState()
    cold_front.active = True
    cold_front.hours_remaining = 100            # stays active through this step
    state = {
        "climate": climate,
        "battery": battery,
        "history": history,
        "criticality_tree": build_criticality_tree(),
        "storm_state": StormState(),
        "coldfront_state": cold_front,
        "last_wind_24h": deque(maxlen=24),
        "rng": RandomLCG(123),
    }
    step(state)

    assert history["temperature_c"][0] == expected_base_temp + COLDFRONT_DELTA_C
