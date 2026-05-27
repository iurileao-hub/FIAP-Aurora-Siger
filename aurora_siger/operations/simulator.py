"""Simulator orchestrator: 1 step + complete horizon (Fase 3, M2).

Builds on M1's deterministic core. M2 adds the consolidation layers:
  * a battery-driven power_factor that throttles consumption targets, composed
    with the 4-stage load shedding (two-layer control, §3.3);
  * stochastic equipment failure with timed auto-repair (§3.6);
  * an OLS energy trend (slope + predicted next delta) and the CRITICAL→SURPLUS
    energy level it feeds (§3.5), recorded each step as output labels.

Determinism per seed is preserved: all randomness still flows through the
single injected RandomLCG, and run_simulation() resets per-module runtime
state so a fresh seeded run never inherits a previous run's failures or modes.
"""

from collections import deque

from aurora_siger.operations.allocation import allocate_energy, power_factor
from aurora_siger.operations.climate import (
    sample_wind, sample_temperature, compute_tau,
    update_panel_factor, StormState, ColdFrontState,
)
from aurora_siger.operations.consumption import current_consumption_kw
from aurora_siger.operations.constants import (
    HOURS_PER_SOL, TOTAL_STEPS, CLEANING_PROB_PER_SOL, FORCE_DIDACTIC_EVENT,
    TREND_WINDOW,
)
from aurora_siger.operations.energy_levels import energy_level
from aurora_siger.operations.failures import maybe_fail, advance_repair, is_operational
from aurora_siger.operations.prediction import fit_energy_trend
from aurora_siger.operations.state import initial_state
from aurora_siger.operations.generation import (
    generate_solar, generate_wind, generate_nuclear,
)
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import MODULES
from aurora_siger.operations.rng import RandomLCG


def _detail_generation(climate):
    """Returns {kind: kW}. Skips broken modules (a failed unit produces nothing)."""
    detail = {"solar": 0.0, "wind": 0.0, "nuclear": 0.0}
    for m in MODULES:
        if not is_operational(m):
            continue
        if m["type"] == "solar_generator":
            detail["solar"] += generate_solar(m, climate)
        elif m["type"] == "wind_generator":
            detail["wind"] += generate_wind(m, climate)
        elif m["type"] == "nuclear_generator":
            detail["nuclear"] += generate_nuclear(m, climate)
    return detail


def _energy_trend(history):
    """(slope, predicted_next_delta) over the recent generation-minus-consumption
    deltas, via the single OLS estimator (§3.2). Short history → (0.0, 0.0)."""
    gen = history["total_generation_kw"]
    con = history["total_consumption_kw"]
    deltas = [g - c for g, c in zip(gen, con)][-TREND_WINDOW:]
    return fit_energy_trend(deltas)


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

    # 1. Climate sampling — wind then temperature MUST stay the first rng draws
    #    (the cold-front wiring test probes the rng in exactly this order).
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

    # 2. Equipment failures + auto-repair (after climate draws; fixed iteration
    #    order over MODULES keeps the rng sequence deterministic).
    for m in MODULES:
        if is_operational(m):
            maybe_fail(m, rng)
        else:
            advance_repair(m)
    broken_count = sum(1 for m in MODULES if not is_operational(m))

    # 3. First control layer: battery-driven power_factor (uses the charge at
    #    the start of the hour, before this step's balance is applied).
    battery_pct = battery["current_charge_kwh"] / battery["max_capacity_kwh"] * 100.0
    pf = power_factor(battery_pct)

    # 4. Generation (broken modules excluded)
    detail = _detail_generation(climate)
    total_generation = detail["solar"] + detail["wind"] + detail["nuclear"]

    # 5. Supply = generation + battery available above the emergency reserve
    battery_available = max(0, battery["current_charge_kwh"] - battery["emergency_reserve_kwh"])
    supply = total_generation + battery_available

    # 6. Second control layer: 4-stage load shedding over the scaled targets
    allocate_energy(criticality, supply_kw=supply, climate=climate, power_factor=pf)

    # 7. Total consumption after allocation (operational modules, scaled draw)
    total_consumption = sum(
        current_consumption_kw(m, climate, power_factor=pf)
        for m in MODULES if is_operational(m)
    )

    # 8. Battery balance, clamped to [0, max]
    balance = total_generation - total_consumption
    battery["current_charge_kwh"] = max(0, min(
        battery["max_capacity_kwh"],
        battery["current_charge_kwh"] + balance,
    ))

    # 9. OLS energy trend → energy level (output labels) + emergency alert
    slope, predicted_delta = _energy_trend(history)
    level = energy_level(battery_pct, slope, predicted_delta)

    alerts = []
    if total_consumption > total_generation + battery_available:
        alerts.append(f"EMERGÊNCIA sol {sol} hora {hour}: oferta insuficiente")

    # 10. Record history
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
    history["energy_level"].append(level)
    history["slope"].append(slope)
    history["predicted_delta"].append(predicted_delta)
    history["broken_count"].append(broken_count)

    # 11. Advance clock
    climate["hour"] += 1
    if climate["hour"] >= HOURS_PER_SOL:
        climate["hour"] = 0
        climate["sol"] += 1


def _reset_modules():
    """Clears per-module runtime state so a fresh run never inherits a previous
    run's failures or modes. MODULES is module-level shared state: allocation
    overwrites current_mode every step, but the failure flags would otherwise
    persist across run_simulation calls and break determinism."""
    for m in MODULES:
        m["broken"] = False
        m["repair_hours_remaining"] = 0
        m["current_mode"] = "adequate"


def init_simulation(seed=42):
    """Builds a ready-to-step simulation state (does not run any step).

    Resets per-module runtime state so a fresh run never inherits a previous
    run's failures or modes (MODULES is module-level shared state). The live
    CLI dashboard and run_simulation both build their state through here.
    """
    rng = RandomLCG(seed)
    _reset_modules()
    climate, battery, history = initial_state()
    return {
        "climate": climate,
        "battery": battery,
        "history": history,
        "criticality_tree": build_criticality_tree(),
        "storm_state": StormState(),
        "coldfront_state": ColdFrontState(),
        "last_wind_24h": deque(maxlen=24),
        "rng": rng,
    }


def run_simulation(seed=42, horizon=TOTAL_STEPS):
    """Runs `horizon` hourly steps. Returns (climate, battery, history).

    seed=42 (default): deterministic. seed=None: entropy from the clock.
    """
    state = init_simulation(seed)
    for _ in range(horizon):
        step(state)
    return state["climate"], state["battery"], state["history"]
