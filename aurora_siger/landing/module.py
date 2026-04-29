"""Module — operational data for one Aurora Siger colony module.

Each prefabricated module is represented by a single :class:`Module` instance
carrying eleven attributes: six static (id, name, type, priority, mass and
cargo criticality) and five volatile (fuel level, distance, speed, sensor
state and current status). The volatile attributes are randomized at the
start of each simulation by :meth:`Module.randomize`.

The ETA is *not* stored: it derives from ``ceil(distance / speed)`` and is
exposed as a property. Rounding to whole hours is deliberate — frequent ties
on ETA activate the secondary sort criteria (priority, fuel level) defined in
:meth:`structures.Vector.sort_multi`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal


# --- Randomization ranges (used by Module.randomize) ---

FUEL_RANGE_MIN = 15.0
"""Lower bound (%) of the fuel-level draw. Below 20 triggers a denial."""

FUEL_RANGE_MAX = 95.0
"""Upper bound (%) of the fuel-level draw."""

SENSORS_OK_PROBABILITY = 0.95
"""Probability that on-board sensors are intact at scenario start."""

DISTANCE_RANGE_MIN = 200.0
DISTANCE_RANGE_MAX = 800.0
"""Orbital approach distance range in km."""

SPEED_RANGE_MIN = 100.0
SPEED_RANGE_MAX = 400.0
"""Approach velocity range in km/h."""

MISSION_START_HOUR = 6
"""Wall-clock hour at which the landing window opens (06:00). Acts as offset
for :attr:`Module.eta_str`."""


# --- Type aliases ---

ModuleType = Literal[
    "command", "life_support", "habitat", "solar", "nuclear", "comms",
    "medical", "food", "logistics", "isru", "workshop", "lab",
]
"""Functional category of a colony module."""

Status = Literal["queued", "landed", "waiting"]
"""Lifecycle state of a module within a landing simulation."""


@dataclass
class Module:
    """One Aurora Siger colony module awaiting landing.

    Attributes are split into:

    - **Static** — ``id``, ``name``, ``type``, ``priority``, ``mass``,
      ``cargo_criticality``. Fixed at construction.
    - **Volatile** — ``fuel_level``, ``distance``, ``speed``, ``sensors_ok``.
      Reseeded on each :meth:`randomize` call.
    - **Lifecycle** — ``status``. Transitions through ``"queued"`` →
      ``"landed"`` or ``"waiting"`` during simulation.
    """

    id: int
    name: str
    type: ModuleType
    priority: int
    fuel_level: float
    mass: float
    cargo_criticality: int
    distance: float
    speed: float
    sensors_ok: bool = True
    status: Status = "queued"

    @property
    def eta(self) -> int:
        """Whole-hour ETA from mission start: ``ceil(distance / speed)``.

        Discretizing to whole hours is intentional — it produces ties that
        activate the secondary sort criteria (priority, fuel level).
        """
        return math.ceil(self.distance / self.speed)

    @property
    def eta_str(self) -> str:
        """ETA formatted as ``HH:00`` with offset of :data:`MISSION_START_HOUR`."""
        return f"{(MISSION_START_HOUR + self.eta) % 24:02d}:00"

    def randomize(self) -> None:
        """Reseed volatile attributes for a fresh scenario."""
        self.fuel_level = round(random.uniform(FUEL_RANGE_MIN, FUEL_RANGE_MAX), 1)
        self.sensors_ok = random.random() < SENSORS_OK_PROBABILITY
        self.distance = round(random.uniform(DISTANCE_RANGE_MIN, DISTANCE_RANGE_MAX), 1)
        self.speed = round(random.uniform(SPEED_RANGE_MIN, SPEED_RANGE_MAX), 1)

    def copy(self) -> Module:
        """Return an independent copy of this module."""
        return Module(
            id=self.id, name=self.name, type=self.type, priority=self.priority,
            fuel_level=self.fuel_level, mass=self.mass,
            cargo_criticality=self.cargo_criticality,
            distance=self.distance, speed=self.speed,
            sensors_ok=self.sensors_ok, status=self.status,
        )

    def __repr__(self) -> str:
        return f"Module({self.id}, {self.name!r}, priority={self.priority}, eta={self.eta_str})"


def _default_modules() -> list[Module]:
    """Build the canonical fleet of twelve Aurora Siger modules.

    Initial volatile values approximate the original mission ETAs (offset
    06:00). They are overwritten by :meth:`Module.randomize` at the start of
    each simulation run.
    """
    return [
        Module(id=1,  name="Comando e Controle",        type="command",      priority=1,  fuel_level=85.0, mass=12000.0, cargo_criticality=5, distance=200.0, speed=400.0),
        Module(id=2,  name="Suporte de Vida (ECLSS)",   type="life_support", priority=2,  fuel_level=78.0, mass=15000.0, cargo_criticality=5, distance=300.0, speed=400.0),
        Module(id=3,  name="Habitação",                 type="habitat",      priority=3,  fuel_level=72.0, mass=18000.0, cargo_criticality=4, distance=500.0, speed=400.0),
        Module(id=4,  name="Energia Solar",             type="solar",        priority=4,  fuel_level=65.0, mass=8000.0,  cargo_criticality=5, distance=350.0, speed=200.0),
        Module(id=5,  name="Energia Nuclear",           type="nuclear",      priority=5,  fuel_level=58.0, mass=22000.0, cargo_criticality=5, distance=500.0, speed=200.0),
        Module(id=6,  name="Comunicações",              type="comms",        priority=6,  fuel_level=55.0, mass=6000.0,  cargo_criticality=4, distance=400.0, speed=400.0),
        Module(id=7,  name="Suporte Médico",            type="medical",      priority=7,  fuel_level=70.0, mass=10000.0, cargo_criticality=4, distance=400.0, speed=200.0),
        Module(id=8,  name="Produção de Alimentos",     type="food",         priority=8,  fuel_level=60.0, mass=14000.0, cargo_criticality=3, distance=650.0, speed=200.0),
        Module(id=9,  name="Logística e Armazenamento", type="logistics",    priority=9,  fuel_level=45.0, mass=25000.0, cargo_criticality=3, distance=750.0, speed=200.0),
        Module(id=10, name="ISRU (Recursos Locais)",    type="isru",         priority=10, fuel_level=42.0, mass=20000.0, cargo_criticality=2, distance=550.0, speed=100.0),
        Module(id=11, name="Oficina e Manutenção",      type="workshop",     priority=11, fuel_level=50.0, mass=16000.0, cargo_criticality=2, distance=500.0, speed=100.0),
        Module(id=12, name="Laboratório Científico",    type="lab",          priority=12, fuel_level=82.0, mass=12000.0, cargo_criticality=2, distance=400.0, speed=100.0),
    ]


DEFAULT_MODULES: list[Module] = _default_modules()
"""Canonical twelve-module fleet. Treat as read-only template — copy via
:meth:`Module.copy` before mutating, since :class:`LandingMission` expects to
reseed volatile state on each run."""
