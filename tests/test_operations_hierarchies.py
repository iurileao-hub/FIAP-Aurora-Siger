from aurora_siger.operations.hierarchies import (
    build_functional_tree, build_criticality_tree,
)
from aurora_siger.operations.modules import MODULES


def test_criticality_tree_has_three_levels():
    root = build_criticality_tree()
    assert [c.name for c in root.children] == ["Vital", "Sustenance", "Expansion"]


def test_both_trees_cover_all_thirteen_modules():
    for build in (build_functional_tree, build_criticality_tree):
        ids = {m["id"] for m in build().leaves()}
        assert ids == {m["id"] for m in MODULES}


def test_trees_reference_same_module_dicts():
    # mutating a module via one tree is visible from MODULES (shared identity)
    tree = build_criticality_tree()
    leaf_mod = tree.find("Habitat").module
    leaf_mod["current_mode"] = "off"
    from aurora_siger.operations.modules import find_module
    assert find_module(3)["current_mode"] == "off"
    leaf_mod["current_mode"] = "adequate"  # restore
