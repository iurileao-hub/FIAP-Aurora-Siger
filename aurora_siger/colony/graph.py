"""Colony infrastructure as a weighted, undirected graph.

Vertices are colony modules (see roster.py, derived from Fase 3); edges are the
network topology (see topology.py). Keeps both an adjacency list (fast traversal)
and an adjacency matrix (O(1) weight lookup) — the two representations the
assignment asks for. Pure data structure: no I/O.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Module:
    """A colony module — a vertex of the infrastructure graph."""

    id: int
    name: str
    type: str
    consumption: float          # kW, "adequate" operating mode
    priority: int               # 1–10, derived from the criticality tier
    capacity: float             # kWh of local storage (network overlay)
    communication_need: int     # 1–10 (network overlay)
    position: Optional[tuple[float, float]] = None
    status: str = "active"


class InfrastructureGraph:
    """Undirected weighted graph over colony modules."""

    def __init__(self) -> None:
        self.adjacency_list: dict[int, list[int]] = defaultdict(list)
        self.modules: dict[int, Module] = {}
        self.module_list: list[Module] = []
        self.edge_weights: dict[str, float] = {}
        self.connection_types: dict[str, str] = {}
        self.adjacency_matrix: list[list[float]] = []
        self.distance_matrix: list[list[float]] = []

    def _get_edge_key(self, id1: int, id2: int) -> str:
        return f"{min(id1, id2)}-{max(id1, id2)}"

    def add_module(self, module: Module) -> None:
        if module.id in self.modules:
            raise ValueError(f"Module {module.id} already exists")
        self.modules[module.id] = module
        self.module_list.append(module)
        self.adjacency_list[module.id] = self.adjacency_list.get(module.id, [])
        self._rebuild_matrices()

    def add_connection(self, id1: int, id2: int, weight: float,
                       connection_type: str = "energy") -> None:
        if id1 not in self.modules or id2 not in self.modules:
            raise ValueError(f"Module not found: {id1} or {id2}")
        if id1 == id2:
            raise ValueError("Cannot connect a module to itself")
        if id2 not in self.adjacency_list[id1]:
            self.adjacency_list[id1].append(id2)
        if id1 not in self.adjacency_list[id2]:
            self.adjacency_list[id2].append(id1)
        key = self._get_edge_key(id1, id2)
        self.edge_weights[key] = weight
        self.connection_types[key] = connection_type
        self._rebuild_matrices()

    def get_neighbors(self, module_id: int) -> list[int]:
        return self.adjacency_list.get(module_id, [])

    def get_weight(self, id1: int, id2: int) -> float:
        if id1 == id2:
            return 0
        return self.edge_weights.get(self._get_edge_key(id1, id2), float("inf"))

    def get_module(self, module_id: int) -> Optional[Module]:
        return self.modules.get(module_id)

    def get_module_count(self) -> int:
        return len(self.module_list)

    def get_connection_count(self) -> int:
        return sum(len(v) for v in self.adjacency_list.values()) // 2

    def get_index(self, module_id: int) -> Optional[int]:
        for i, mod in enumerate(self.module_list):
            if mod.id == module_id:
                return i
        return None

    def get_adjacency_matrix(self) -> list[list[float]]:
        return self.adjacency_matrix

    def get_distance_matrix(self) -> list[list[float]]:
        return self.distance_matrix

    def _rebuild_matrices(self) -> None:
        n = len(self.module_list)
        idx = {mod.id: i for i, mod in enumerate(self.module_list)}
        self.adjacency_matrix = [[0.0] * n for _ in range(n)]
        self.distance_matrix = [[float("inf")] * n for _ in range(n)]
        for i in range(n):
            self.distance_matrix[i][i] = 0
        for id1, neighbors in self.adjacency_list.items():
            if id1 not in idx:
                continue
            i = idx[id1]
            for id2 in neighbors:
                if id2 not in idx:
                    continue
                j = idx[id2]
                w = self.edge_weights.get(self._get_edge_key(id1, id2), 1)
                self.adjacency_matrix[i][j] = float(w)
                self.distance_matrix[i][j] = float(w)
