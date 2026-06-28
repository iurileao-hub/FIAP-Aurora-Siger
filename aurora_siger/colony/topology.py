"""The Fase 4 network overlay over the 13 Fase 3 modules.

Fase 3 modules carry no topology — no positions, no edges, no storage capacity,
no communication need. This module owns those network attributes and wires the
canonical colony graph. Edge weights model distance / transmission cost.
"""

from aurora_siger.colony.graph import InfrastructureGraph, Module
from aurora_siger.colony.roster import derived_attributes

POSITIONS: dict[int, tuple[float, float]] = {
    1: (3, 3), 2: (2, 4), 3: (3, 4), 4: (0, 4), 5: (0, 2), 6: (4, 2),
    7: (2, 3), 8: (1, 1), 9: (1, 5), 10: (0, 1), 11: (1, 3), 12: (4, 4),
    13: (0, 0),
}

STORAGE_CAPACITY: dict[int, float] = {
    1: 15, 2: 20, 3: 30, 4: 10, 5: 15, 6: 5, 7: 8,
    8: 20, 9: 500, 10: 40, 11: 5, 12: 10, 13: 5,
}

COMM_NEED: dict[int, int] = {
    1: 10, 2: 4, 3: 5, 4: 2, 5: 2, 6: 10, 7: 7,
    8: 6, 9: 4, 10: 5, 11: 4, 12: 8, 13: 2,
}

EDGES: list[tuple[int, int, float, str]] = [
    (5, 1, 2, "energy"), (5, 2, 2, "energy"), (5, 3, 3, "energy"),
    (4, 3, 2, "energy"), (4, 8, 2, "energy"), (4, 9, 2, "energy"),
    (5, 9, 2, "energy"), (13, 9, 3, "energy"),
    (2, 3, 1, "life"), (3, 7, 1, "life"), (2, 7, 2, "life"),
    (1, 6, 2, "data"), (1, 12, 3, "data"), (1, 3, 2, "data"), (6, 7, 3, "data"),
    (8, 10, 2, "energy"), (10, 11, 2, "data"), (11, 9, 2, "energy"),
    (12, 8, 2, "data"), (11, 5, 3, "energy"),
]


def build_graph() -> InfrastructureGraph:
    """Assembles the canonical 13-node colony graph (roster + overlay + edges)."""
    g = InfrastructureGraph()
    for mid in range(1, 14):
        attrs = derived_attributes(mid)
        g.add_module(Module(
            id=attrs["id"],
            name=attrs["name"],
            type=attrs["type"],
            consumption=attrs["consumption"],
            priority=attrs["priority"],
            capacity=STORAGE_CAPACITY[mid],
            communication_need=COMM_NEED[mid],
            position=POSITIONS[mid],
        ))
    for id1, id2, weight, conn_type in EDGES:
        g.add_connection(id1, id2, weight, conn_type)
    return g
