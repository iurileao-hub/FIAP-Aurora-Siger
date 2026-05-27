from aurora_siger.operations.rng import RandomLCG
from aurora_siger.operations.failures import (
    is_operational, maybe_fail, advance_repair,
)


def _fresh_module():
    return {"id": 1, "name": "Test", "broken": False, "repair_hours_remaining": 0}


def test_fresh_module_is_operational():
    assert is_operational(_fresh_module()) is True


def test_maybe_fail_is_deterministic_per_seed():
    a, b = RandomLCG(42), RandomLCG(42)
    ma, mb = _fresh_module(), _fresh_module()
    rolls_a = [maybe_fail(_fresh_module(), a) for _ in range(50)]
    rolls_b = [maybe_fail(_fresh_module(), b) for _ in range(50)]
    assert rolls_a == rolls_b


def test_failure_sets_broken_and_schedules_repair():
    # find a seed/sequence that fails: drive rng until a failure is observed
    rng = RandomLCG(7)
    mod = _fresh_module()
    for _ in range(100000):
        if maybe_fail(mod, rng):
            break
    assert mod["broken"] is True
    assert is_operational(mod) is False
    assert mod["repair_hours_remaining"] >= 1


def test_advance_repair_restores_after_countdown():
    mod = {"id": 1, "broken": True, "repair_hours_remaining": 2}
    assert advance_repair(mod) is False  # 2 -> 1, still broken
    assert mod["broken"] is True
    assert advance_repair(mod) is True   # 1 -> 0, repaired
    assert mod["broken"] is False
    assert is_operational(mod) is True


def test_advance_repair_noop_on_operational_module():
    mod = _fresh_module()
    assert advance_repair(mod) is False
    assert is_operational(mod) is True
