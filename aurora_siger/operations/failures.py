"""Stochastic equipment failure + timed auto-repair (Fase 3 event, §3.6).

Harvested from the team `main` branch's broken/active flags
(colonia_aurora/modules/module.py), but WITHOUT the crew system: repair is an
automatic background process whose duration is sampled when the failure
happens. All randomness flows through the injected RandomLCG, so failures are
deterministic per seed like everything else in the simulation.

Pure functions over a module dict. A module carries two runtime fields:
  * "broken" (bool) — out of generation/consumption while True;
  * "repair_hours_remaining" (int) — ticks down to 0, then the module is back.
Both default to absent → operational, so callers need not pre-initialize them
(run_simulation resets them explicitly to keep runs independent).
"""

from aurora_siger.operations.constants import (
    FAILURE_PROB_PER_HOUR, REPAIR_DURATION_HOURS,
)
from aurora_siger.operations.rng import RandomLCG


def is_operational(module: dict) -> bool:
    """A module is operational unless it is currently broken."""
    return not module.get("broken", False)


def maybe_fail(module: dict, rng: RandomLCG) -> bool:
    """Rolls a failure for one operational module (one hour).

    On failure: marks it broken and samples a repair countdown. Returns True
    iff it just failed. A module already broken is left untouched (returns
    False) — repair is handled by advance_repair.
    """
    if module.get("broken", False):
        return False
    if rng.random() < FAILURE_PROB_PER_HOUR:
        module["broken"] = True
        lo, hi = REPAIR_DURATION_HOURS
        module["repair_hours_remaining"] = rng.randint(lo, hi)
        return True
    return False


def advance_repair(module: dict) -> bool:
    """Ticks a broken module's repair timer by one hour; restores it when the
    countdown reaches 0. Returns True iff it just came back online. A no-op on
    operational modules (returns False).
    """
    if not module.get("broken", False):
        return False
    module["repair_hours_remaining"] -= 1
    if module["repair_hours_remaining"] <= 0:
        module["broken"] = False
        module["repair_hours_remaining"] = 0
        return True
    return False
