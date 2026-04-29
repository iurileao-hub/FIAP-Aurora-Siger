"""Landing and base stabilization domain — Phase 2 (MGPEB).

This subpackage models the descent of the twelve prefabricated modules of the
Aurora Siger Mars colony. It exposes:

- ``Module``               — operational data for a single colony module
- ``Vector``, ``Queue``, ``Stack`` — linear data structures with search/sort
- ``evaluate``             — pure boolean authorization rule F ∧ A ∧ (L ∨ E) ∧ S
- ``Alert``                — record of a denied landing
- ``LandingMission``       — stateful orchestrator of the queue, decisions and alerts
- physics functions        — descent altitude, fuel consumption, solar energy, surface temperature
"""

from aurora_siger.landing.authorization import (
    Alert,
    AuthorizationResult,
    EMERGENCY_CRITICALITY,
    FUEL_THRESHOLD,
    evaluate,
)
from aurora_siger.landing.mission import LandingMission, SimulationReport
from aurora_siger.landing.module import (
    DEFAULT_MODULES,
    MISSION_START_HOUR,
    Module,
    ModuleType,
    Status,
)
from aurora_siger.landing.physics import (
    descent_altitude,
    fuel_consumption,
    solar_energy,
    surface_temperature,
)
from aurora_siger.landing.structures import Queue, Stack, Vector

__all__ = [
    "Alert",
    "AuthorizationResult",
    "DEFAULT_MODULES",
    "EMERGENCY_CRITICALITY",
    "FUEL_THRESHOLD",
    "LandingMission",
    "MISSION_START_HOUR",
    "Module",
    "ModuleType",
    "Queue",
    "SimulationReport",
    "Stack",
    "Status",
    "Vector",
    "descent_altitude",
    "evaluate",
    "fuel_consumption",
    "solar_energy",
    "surface_temperature",
]
