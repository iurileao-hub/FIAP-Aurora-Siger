"""Tests for the boolean landing-authorization rule.

The rule is ``AUTHORIZED = F ∧ A ∧ (L ∨ E) ∧ S`` — five boolean inputs, 32
rows in the truth table. We exercise the rule end to end via parametrized
truth-table tests, plus targeted assertions on each failure reason.
"""

import pytest

from aurora_siger.landing.authorization import (
    Alert,
    AuthorizationResult,
    EMERGENCY_CRITICALITY,
    FUEL_THRESHOLD,
    evaluate,
)
from aurora_siger.landing.module import Module


def make_module(*, fuel_ok: bool, sensors_ok: bool, emergency: bool) -> Module:
    """Construct a Module that exposes the three module-side rule variables."""
    return Module(
        id=1, name="Test", type="lab", priority=5,
        fuel_level=80.0 if fuel_ok else (FUEL_THRESHOLD - 5.0),
        mass=1000.0,
        cargo_criticality=EMERGENCY_CRITICALITY if emergency else 2,
        distance=400.0, speed=200.0,
        sensors_ok=sensors_ok,
    )


def make_conditions(*, atmosphere_ok: bool, zone_free: bool) -> dict[str, bool]:
    return {"atmosphere_ok": atmosphere_ok, "landing_zone_free": zone_free}


# --- Truth table: 32 combinations of (F, A, L, E, S) ---
# AUTHORIZED = F ∧ A ∧ (L ∨ E) ∧ S


def _expected(f: bool, a: bool, l: bool, e: bool, s: bool) -> bool:
    return f and a and (l or e) and s


@pytest.mark.parametrize("f", [False, True])
@pytest.mark.parametrize("a", [False, True])
@pytest.mark.parametrize("l", [False, True])
@pytest.mark.parametrize("e", [False, True])
@pytest.mark.parametrize("s", [False, True])
def test_truth_table(f, a, l, e, s):
    module = make_module(fuel_ok=f, sensors_ok=s, emergency=e)
    conditions = make_conditions(atmosphere_ok=a, zone_free=l)
    result = evaluate(module, conditions)
    assert result.authorized is _expected(f, a, l, e, s)


# --- Boundary on FUEL_THRESHOLD ---

def test_fuel_at_threshold_is_authorized():
    # Boundary inclusive: fuel_level == FUEL_THRESHOLD must pass.
    module = Module(
        id=1, name="Edge", type="lab", priority=5,
        fuel_level=FUEL_THRESHOLD, mass=1000.0, cargo_criticality=3,
        distance=400.0, speed=200.0, sensors_ok=True,
    )
    result = evaluate(module, make_conditions(atmosphere_ok=True, zone_free=True))
    assert result.authorized


def test_fuel_just_below_threshold_is_denied():
    module = Module(
        id=1, name="Edge", type="lab", priority=5,
        fuel_level=FUEL_THRESHOLD - 0.1, mass=1000.0, cargo_criticality=3,
        distance=400.0, speed=200.0, sensors_ok=True,
    )
    result = evaluate(module, make_conditions(atmosphere_ok=True, zone_free=True))
    assert not result.authorized
    assert any("Combustível" in r for r in result.reasons)


# --- Emergency bypass: cargo_criticality == 5 overrides zone occupied ---

def test_emergency_bypasses_occupied_zone():
    module = make_module(fuel_ok=True, sensors_ok=True, emergency=True)
    result = evaluate(module, make_conditions(atmosphere_ok=True, zone_free=False))
    assert result.authorized


def test_non_emergency_blocked_by_occupied_zone():
    module = make_module(fuel_ok=True, sensors_ok=True, emergency=False)
    result = evaluate(module, make_conditions(atmosphere_ok=True, zone_free=False))
    assert not result.authorized
    assert any("Zona" in r for r in result.reasons)


def test_emergency_does_not_bypass_atmosphere():
    """Emergency only relaxes (L ∨ E); A must still hold."""
    module = make_module(fuel_ok=True, sensors_ok=True, emergency=True)
    result = evaluate(module, make_conditions(atmosphere_ok=False, zone_free=True))
    assert not result.authorized
    assert any("atmosféricas" in r for r in result.reasons)


def test_emergency_does_not_bypass_sensors():
    """Emergency only relaxes (L ∨ E); S must still hold."""
    module = make_module(fuel_ok=True, sensors_ok=False, emergency=True)
    result = evaluate(module, make_conditions(atmosphere_ok=True, zone_free=True))
    assert not result.authorized
    assert any("sensores" in r for r in result.reasons)


# --- Reason messages ---

def test_reasons_empty_when_authorized():
    module = make_module(fuel_ok=True, sensors_ok=True, emergency=False)
    result = evaluate(module, make_conditions(atmosphere_ok=True, zone_free=True))
    assert result.reasons == []


def test_all_failures_reported_simultaneously():
    """A worst-case module accumulates every failure reason."""
    module = make_module(fuel_ok=False, sensors_ok=False, emergency=False)
    result = evaluate(module, make_conditions(atmosphere_ok=False, zone_free=False))
    assert not result.authorized
    text = " ; ".join(result.reasons)
    assert "Combustível" in text
    assert "atmosféricas" in text
    assert "Zona" in text
    assert "sensores" in text


def test_reason_order_is_stable():
    """Failure reasons appear in canonical order: fuel → atmosphere → zone → sensors."""
    module = make_module(fuel_ok=False, sensors_ok=False, emergency=False)
    result = evaluate(module, make_conditions(atmosphere_ok=False, zone_free=False))
    keywords = ["Combustível", "atmosféricas", "Zona", "sensores"]
    indices = [next(i for i, r in enumerate(result.reasons) if kw in r) for kw in keywords]
    assert indices == sorted(indices)


# --- Dataclass invariants ---

def test_authorization_result_is_frozen():
    result = AuthorizationResult(authorized=True, reasons=[])
    with pytest.raises(Exception):
        result.authorized = False  # type: ignore[misc]


def test_alert_is_frozen():
    alert = Alert(module_id=1, module_name="X", reason="r", timestamp="07:00")
    with pytest.raises(Exception):
        alert.reason = "other"  # type: ignore[misc]
