"""Tests for the Module dataclass and the canonical fleet."""

import random

import pytest

from aurora_siger.landing.module import (
    DEFAULT_MODULES,
    FUEL_RANGE_MAX,
    FUEL_RANGE_MIN,
    MISSION_START_HOUR,
    Module,
)


def make_module(**overrides) -> Module:
    """Build a Module for tests with sensible defaults; override per case."""
    defaults = dict(
        id=99, name="Test", type="lab", priority=5,
        fuel_level=80.0, mass=1000.0, cargo_criticality=3,
        distance=400.0, speed=200.0,
    )
    defaults.update(overrides)
    return Module(**defaults)


# --- ETA derivation ---

def test_eta_is_ceil_of_distance_over_speed():
    m = make_module(distance=500.0, speed=200.0)  # 500/200 = 2.5 → ceil = 3
    assert m.eta == 3


def test_eta_rounds_up_even_for_exact_division():
    # 200/100 = 2.0 → ceil = 2 (no rounding up needed)
    m = make_module(distance=200.0, speed=100.0)
    assert m.eta == 2


def test_eta_str_offsets_from_mission_start_hour():
    m = make_module(distance=400.0, speed=200.0)  # eta = 2
    expected_hour = (MISSION_START_HOUR + 2) % 24
    assert m.eta_str == f"{expected_hour:02d}:00"


def test_eta_str_format_is_always_hh00():
    # eta_str is whole-hour by construction; no half-hour artefacts.
    for distance in (200.0, 350.0, 500.0, 750.0):
        for speed in (100.0, 200.0, 400.0):
            m = make_module(distance=distance, speed=speed)
            assert m.eta_str.endswith(":00")


# --- copy() independence ---

def test_copy_produces_independent_instance():
    original = make_module(fuel_level=60.0)
    clone = original.copy()
    clone.fuel_level = 30.0
    assert original.fuel_level == 60.0
    assert clone.fuel_level == 30.0


def test_copy_preserves_all_attributes():
    original = make_module(
        fuel_level=42.5, sensors_ok=False, status="waiting", priority=7,
    )
    clone = original.copy()
    assert clone == original  # @dataclass equality


# --- randomize() bounds ---

def test_randomize_keeps_fuel_level_in_range():
    m = make_module()
    random.seed(42)
    for _ in range(50):
        m.randomize()
        assert FUEL_RANGE_MIN <= m.fuel_level <= FUEL_RANGE_MAX


def test_randomize_changes_volatile_attributes():
    m = make_module(fuel_level=80.0, distance=400.0, speed=200.0, sensors_ok=True)
    random.seed(0)
    m.randomize()
    # At least one volatile attribute should change with this seed.
    changed = (
        m.fuel_level != 80.0
        or m.distance != 400.0
        or m.speed != 200.0
    )
    assert changed


def test_randomize_does_not_touch_static_attributes():
    m = make_module(id=5, name="Stays", type="solar", priority=4, mass=8000.0,
                    cargo_criticality=5)
    m.randomize()
    assert m.id == 5
    assert m.name == "Stays"
    assert m.type == "solar"
    assert m.priority == 4
    assert m.mass == 8000.0
    assert m.cargo_criticality == 5


# --- DEFAULT_MODULES fleet ---

def test_default_modules_has_twelve_entries():
    assert len(DEFAULT_MODULES) == 12


def test_default_modules_have_unique_ids_one_through_twelve():
    ids = sorted(m.id for m in DEFAULT_MODULES)
    assert ids == list(range(1, 13))


def test_default_modules_have_unique_priorities():
    priorities = sorted(m.priority for m in DEFAULT_MODULES)
    assert priorities == list(range(1, 13))


@pytest.mark.parametrize("module_type", [
    "command", "life_support", "habitat", "solar", "nuclear", "comms",
    "medical", "food", "logistics", "isru", "workshop", "lab",
])
def test_default_modules_cover_every_type(module_type):
    """Each of the twelve canonical types must appear exactly once."""
    matches = [m for m in DEFAULT_MODULES if m.type == module_type]
    assert len(matches) == 1
