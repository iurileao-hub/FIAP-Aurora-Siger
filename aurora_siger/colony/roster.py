"""Derives the colony graph's nodes from the Fase 3 module roster.

Single source of truth for module identity is aurora_siger.operations.MODULES
(13 modules). Priority is derived from the Fase 3 criticality tree so there is no
second priority table to drift. This module READS operations and never mutates it.
"""

from aurora_siger.operations.constants import GENERATOR_TYPES
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import MODULES, find_module

PRIORITY_BY_TIER: dict[str, int] = {
    "Vital": 10,
    "Sustenance": 7,
    "Expansion": 4,
}


def _criticality_index() -> dict[int, str]:
    """Maps module id -> criticality tier name by walking the criticality tree."""
    root = build_criticality_tree()
    index: dict[int, str] = {}
    for tier_node in root.children:               # Vital / Sustenance / Expansion
        for leaf in tier_node.children:
            if leaf.module is not None:
                index[leaf.module["id"]] = tier_node.name
    return index


_CRIT = _criticality_index()


def criticality_of(module_id: int) -> str:
    return _CRIT[module_id]


def priority_of(module_id: int) -> int:
    return PRIORITY_BY_TIER[criticality_of(module_id)]


def adequate_consumption(module: dict) -> float:
    return module["consumption_by_mode"]["adequate"]


def generation_capacity_kw() -> float:
    """Installed generation = sum of the generators' max_capacity_kw (210 kW)."""
    return float(sum(
        m["max_capacity_kw"] for m in MODULES if m["type"] in GENERATOR_TYPES
    ))


def derived_attributes(module_id: int) -> dict:
    m = find_module(module_id)
    return {
        "id": m["id"],
        "name": m["name"],
        "type": m["type"],
        "consumption": adequate_consumption(m),
        "priority": priority_of(module_id),
    }
