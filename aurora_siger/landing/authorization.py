"""Boolean landing-authorization rule — pure, side-effect-free.

The rule is the heart of the MGPEB and the central argument of Section 5 of
the report ("inspectable rules over opaque classifiers"). Keeping it free of
I/O and global state lets that argument materialize: anyone can audit the
function in isolation and verify it against the truth table.

The rule:

    AUTHORIZED = F ∧ A ∧ (L ∨ E) ∧ S

where

    F = fuel_ok       (module.fuel_level >= 20)
    A = atmosphere_ok (environmental flag)
    L = zone_free     (environmental flag)
    E = emergency    (module.cargo_criticality == 5) — bypass for L
    S = sensors_ok    (module.sensors_ok)

Logging of denials is delegated to :class:`mission.LandingMission`, which
turns each :class:`AuthorizationResult` into an :class:`Alert` on its
internal stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aurora_siger.landing.module import Module


FUEL_THRESHOLD = 20.0
"""Minimum ``fuel_level`` (%) required for a controlled descent."""

EMERGENCY_CRITICALITY = 5
"""Cargo criticality value that activates the zone-occupied bypass."""


@dataclass(frozen=True)
class AuthorizationResult:
    """Outcome of evaluating the landing rule for a single module.

    Attributes:
        authorized: True if every condition holds.
        reasons: Human-readable failure causes, empty when authorized. Order
            is stable (fuel → atmosphere → zone → sensors).
    """

    authorized: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Alert:
    """Auditable record of a denied landing.

    Stored on :attr:`mission.LandingMission.alert_stack` in LIFO order so the
    operator inspects the most recent denial first.
    """

    module_id: int
    module_name: str
    reason: str
    timestamp: str  # HH:MM (the module's eta_str at decision time)


def evaluate(module: Module, conditions: dict[str, bool]) -> AuthorizationResult:
    """Apply the boolean rule ``F ∧ A ∧ (L ∨ E) ∧ S`` to a single module.

    Args:
        module: The module being evaluated.
        conditions: Mapping with keys ``"atmosphere_ok"`` and
            ``"landing_zone_free"`` (per-mission environmental flags).

    Returns:
        An :class:`AuthorizationResult` carrying both the boolean verdict and
        the ordered list of failure reasons.
    """
    fuel_ok = module.fuel_level >= FUEL_THRESHOLD
    atmosphere_ok = conditions["atmosphere_ok"]
    zone_free = conditions["landing_zone_free"]
    sensors_ok = module.sensors_ok
    emergency = module.cargo_criticality == EMERGENCY_CRITICALITY

    authorized = fuel_ok and atmosphere_ok and (zone_free or emergency) and sensors_ok

    reasons: list[str] = []
    if not authorized:
        if not fuel_ok:
            reasons.append(f"Combustível insuficiente ({module.fuel_level:.1f}%)")
        if not atmosphere_ok:
            reasons.append("Condições atmosféricas desfavoráveis")
        if not zone_free and not emergency:
            reasons.append("Zona de pouso ocupada")
        if not sensors_ok:
            reasons.append("Falha nos sensores")

    return AuthorizationResult(authorized=authorized, reasons=reasons)
