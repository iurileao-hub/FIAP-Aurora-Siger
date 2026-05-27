from aurora_siger.operations.allocation import allocate_energy
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import find_module

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
