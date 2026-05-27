from aurora_siger.operations.allocation import allocate_energy, power_factor
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import find_module, MODULES

WARM = {"temperature_c": 25.0}  # no thermal term, keeps arithmetic simple


def _reset_modes():
    for mid in range(1, 14):
        find_module(mid)["current_mode"] = "adequate"


def test_abundant_supply_keeps_everyone_at_least_adequate():
    _reset_modes()
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=10_000, climate=WARM)
    assert all(find_module(i)["current_mode"] in ("adequate", "surplus")
               for i in range(1, 14))


def test_scarce_supply_never_shuts_vital():
    _reset_modes()
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=1.0, climate=WARM)
    vital_ids = [1, 2, 7, 3]  # Command, ECLSS, Medical, Habitat
    assert all(find_module(i)["current_mode"] != "off" for i in vital_ids)


def test_expansion_sheds_before_vital():
    _reset_modes()
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=20.0, climate=WARM)
    # Science Lab (id 12, Expansion) should be off before any Vital module
    assert find_module(12)["current_mode"] == "off"
    assert find_module(1)["current_mode"] != "off"


def test_power_factor_is_piecewise_and_monotonic():
    assert power_factor(80.0) == 1.0
    assert power_factor(50.0) == 1.0
    assert power_factor(5.0) == 0.2
    # monotonic non-decreasing in battery %
    pts = [power_factor(p) for p in range(0, 101, 5)]
    assert all(b >= a for a, b in zip(pts, pts[1:]))
    assert all(0.2 <= v <= 1.0 for v in pts)


def test_low_power_factor_lets_more_fit_under_same_supply():
    # With the throttle on (pf<1), the same scarce supply keeps more modules
    # out of 'off' than at full power, because each module's target is smaller.
    def off_count(pf):
        for mid in range(1, 14):
            find_module(mid)["current_mode"] = "adequate"
        tree = build_criticality_tree()
        allocate_energy(tree, supply_kw=40.0, climate=WARM, power_factor=pf)
        return sum(1 for m in MODULES if m["current_mode"] == "off")

    assert off_count(0.4) <= off_count(1.0)


def test_allocation_default_power_factor_matches_m1():
    # default power_factor=1.0 reproduces the M1 behavior exactly
    for mid in range(1, 14):
        find_module(mid)["current_mode"] = "adequate"
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=20.0, climate=WARM)  # no power_factor arg
    assert find_module(12)["current_mode"] == "off"
    assert find_module(1)["current_mode"] != "off"
