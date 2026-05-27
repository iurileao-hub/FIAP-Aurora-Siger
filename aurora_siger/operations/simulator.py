"""Simulator orchestrator: 1 step + complete horizon.

Ported from the team's `iuri` branch, with two changes: randomness flows
through an injected RandomLCG (seeded, deterministic, no global state) and a
ColdFrontState event is advanced each step and applied to the temperature.
"""

from collections import deque

from aurora_siger.operations.allocation import allocate_energy
from aurora_siger.operations.climate import (
    sample_wind, sample_temperature, compute_tau,
    update_panel_factor, StormState, ColdFrontState,
)
from aurora_siger.operations.consumption import current_consumption_kw
from aurora_siger.operations.constants import (
    HOURS_PER_SOL, TOTAL_STEPS, CLEANING_PROB_PER_SOL, FORCE_DIDACTIC_EVENT,
)
from aurora_siger.operations.state import initial_state
from aurora_siger.operations.generation import (
    generate_solar, generate_wind, generate_nuclear,
)
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import MODULES
from aurora_siger.operations.rng import RandomLCG


def _detail_generation(climate):
    """Returns {kind: kW}. Iterates MODULES (generation depends only on type)."""
    detail = {"solar": 0.0, "wind": 0.0, "nuclear": 0.0}
    for m in MODULES:
        if m["type"] == "solar_generator":
            detail["solar"] += generate_solar(m, climate)
        elif m["type"] == "wind_generator":
            detail["wind"] += generate_wind(m, climate)
        elif m["type"] == "nuclear_generator":
            detail["nuclear"] += generate_nuclear(m, climate)
    return detail


def step(state):
    """Advances the simulation by 1 hour. Mutates `state` in place."""
    climate = state["climate"]
    battery = state["battery"]
    history = state["history"]
    criticality = state["criticality_tree"]
    storm_state = state["storm_state"]
    coldfront_state = state["coldfront_state"]
    last_wind_24h = state["last_wind_24h"]
    rng = state["rng"]

    sol = climate["sol"]
    hour = climate["hour"]

    # 1. Climate sampling (all randomness via the injected LCG)
    wind = sample_wind(hour, rng)
    temperature = sample_temperature(sol, hour, rng)
    last_wind_24h.append(wind)
    wind_max_24h = max(last_wind_24h)

    storm_state.advance(wind_max_24h, sol, hour, rng, force_event=FORCE_DIDACTIC_EVENT)
    coldfront_state.advance(sol, hour, rng)
    temperature += coldfront_state.temperature_offset()

    tau = compute_tau(storm_state.state, wind)

    if hour == 0:
        cleaning_drawn = rng.random() < CLEANING_PROB_PER_SOL
        climate["panel_factor"] = update_panel_factor(
            climate["panel_factor"], cleaning_drawn, rng
        )

    climate["wind_ms"] = wind
    climate["temperature_c"] = temperature
    climate["storm"] = storm_state.state
    climate["tau"] = tau

    # 2. Generation
    detail = _detail_generation(climate)
    total_generation = detail["solar"] + detail["wind"] + detail["nuclear"]

    # 3. Supply = generation + battery above the emergency reserve
    battery_available = max(0, battery["current_charge_kwh"] - battery["emergency_reserve_kwh"])
    supply = total_generation + battery_available

    # 4. Allocation (4-stage load shedding)
    allocate_energy(criticality, supply_kw=supply, climate=climate)

    # 5. Total consumption after allocation
    total_consumption = sum(current_consumption_kw(m, climate) for m in MODULES)

    # 6. Battery balance, clamped to [0, max]
    balance = total_generation - total_consumption
    battery["current_charge_kwh"] = max(0, min(
        battery["max_capacity_kwh"],
        battery["current_charge_kwh"] + balance,
    ))

    # 7. Emergency alert
    alerts = []
    if total_consumption > total_generation + battery_available:
        alerts.append(f"EMERGÊNCIA sol {sol} hora {hour}: oferta insuficiente")

    # 8. Record history
    history["wind_ms"].append(wind)
    history["temperature_c"].append(temperature)
    history["storm"].append(storm_state.state)
    history["tau"].append(tau)
    history["solar_generation_kw"].append(detail["solar"])
    history["wind_generation_kw"].append(detail["wind"])
    history["nuclear_generation_kw"].append(detail["nuclear"])
    history["total_generation_kw"].append(total_generation)
    history["total_consumption_kw"].append(total_consumption)
    history["battery_charge_kwh"].append(battery["current_charge_kwh"])
    history["modes_summary"].append({m["name"]: m["current_mode"] for m in MODULES})
    history["alerts"].append(alerts)

    # 9. Advance clock
    climate["hour"] += 1
    if climate["hour"] >= HOURS_PER_SOL:
        climate["hour"] = 0
        climate["sol"] += 1


def run_simulation(seed=42, horizon=TOTAL_STEPS):
    """Runs `horizon` hourly steps. Returns (climate, battery, history).

    seed=42 (default): deterministic. seed=None: entropy from the clock.
    """
    rng = RandomLCG(seed)
    climate, battery, history = initial_state()
    state = {
        "climate": climate,
        "battery": battery,
        "history": history,
        "criticality_tree": build_criticality_tree(),
        "storm_state": StormState(),
        "coldfront_state": ColdFrontState(),
        "last_wind_24h": deque(maxlen=24),
        "rng": rng,
    }
    for _ in range(horizon):
        step(state)
    return climate, battery, history
