"""Integration tests for LandingMission — orchestration of queue, decisions and alerts."""

import random

import pytest

from aurora_siger.landing.authorization import Alert
from aurora_siger.landing.mission import LandingMission
from aurora_siger.landing.module import DEFAULT_MODULES, Module


def _module(**overrides) -> Module:
    defaults = dict(
        id=1, name="M", type="lab", priority=5,
        fuel_level=80.0, mass=1000.0, cargo_criticality=3,
        distance=400.0, speed=200.0, sensors_ok=True,
    )
    defaults.update(overrides)
    return Module(**defaults)


# --- Construction ---

def test_from_defaults_seeds_twelve_modules():
    mission = LandingMission.from_defaults()
    assert mission.landing_queue.size() == 12


def test_from_defaults_does_not_share_state_with_DEFAULT_MODULES():
    """Mutating a queued module must not leak into the canonical fleet."""
    mission = LandingMission.from_defaults()
    queued = mission.landing_queue.get(0)
    queued.fuel_level = 0.0
    canonical = next(m for m in DEFAULT_MODULES if m.id == queued.id)
    assert canonical.fuel_level != 0.0


# --- Simulate: happy path ---

def test_simulate_drains_queue():
    mission = LandingMission(
        modules=[_module(id=1), _module(id=2), _module(id=3)],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    mission.simulate()
    assert mission.landing_queue.is_empty()


def test_simulate_authorizes_all_when_conditions_perfect():
    mission = LandingMission(
        modules=[_module(id=i) for i in range(1, 4)],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    report = mission.simulate()
    assert len(report.landed) == 3
    assert len(report.waiting) == 0
    assert len(report.alerts) == 0


def test_simulate_blocks_all_when_atmosphere_fails():
    mission = LandingMission(
        modules=[_module(id=i) for i in range(1, 4)],
        conditions={"atmosphere_ok": False, "landing_zone_free": True},
    )
    report = mission.simulate()
    assert len(report.landed) == 0
    assert len(report.waiting) == 3
    assert len(report.alerts) == 3


def test_simulate_updates_module_status():
    mission = LandingMission(
        modules=[_module(id=1, sensors_ok=True), _module(id=2, sensors_ok=False)],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    mission.simulate()
    landed = mission.landed_modules.find_by_id(1)
    waiting = mission.waiting_modules.find_by_id(2)
    assert landed.status == "landed"
    assert waiting.status == "waiting"


# --- Alert stack semantics ---

def test_alert_stack_is_lifo_after_simulation():
    mission = LandingMission(
        modules=[
            _module(id=1, sensors_ok=False),  # blocked first
            _module(id=2, sensors_ok=False),  # blocked second
        ],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    mission.simulate(sort_first=False)  # preserve enqueue order
    top = mission.alert_stack.peek()
    assert isinstance(top, Alert)
    assert top.module_id == 2  # most recent denial sits on top


def test_alerts_match_waiting_modules():
    mission = LandingMission(
        modules=[_module(id=i, sensors_ok=False) for i in (1, 2, 3)],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    report = mission.simulate()
    waiting_ids = sorted(m.id for m in report.waiting)
    alert_ids = sorted(a.module_id for a in report.alerts)
    assert waiting_ids == alert_ids


# --- Sort-before-simulation ---

def test_simulate_sorts_by_eta_when_sort_first_true():
    """ETA-1 module should land before ETA-2 even if enqueued last."""
    mission = LandingMission(
        modules=[
            _module(id=1, distance=400.0, speed=200.0),  # eta = 2
            _module(id=2, distance=200.0, speed=200.0),  # eta = 1
        ],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    report = mission.simulate(sort_first=True)
    assert [m.id for m in report.landed] == [2, 1]


def test_simulate_preserves_enqueue_order_when_sort_first_false():
    mission = LandingMission(
        modules=[
            _module(id=1, distance=400.0, speed=200.0),  # eta = 2
            _module(id=2, distance=200.0, speed=200.0),  # eta = 1
        ],
        conditions={"atmosphere_ok": True, "landing_zone_free": True},
    )
    report = mission.simulate(sort_first=False)
    assert [m.id for m in report.landed] == [1, 2]


# --- Reload ---

def test_reload_resets_all_structures():
    mission = LandingMission.from_defaults()
    mission.simulate()
    assert mission.landing_queue.is_empty()
    assert mission.landed_modules.size() > 0

    mission.reload()
    assert mission.landing_queue.size() == 12
    assert mission.landed_modules.is_empty()
    assert mission.waiting_modules.is_empty()
    assert mission.alert_stack.is_empty()


# --- Randomize scenario ---

def test_randomize_scenario_changes_volatile_state():
    random.seed(0)
    mission = LandingMission.from_defaults()
    before = [(m.fuel_level, m.distance, m.speed) for m in mission.landing_queue]
    mission.randomize_scenario()
    after = [(m.fuel_level, m.distance, m.speed) for m in mission.landing_queue]
    assert before != after  # at least one tuple should differ
