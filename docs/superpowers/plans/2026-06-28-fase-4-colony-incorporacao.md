# Fase 4 — Incorporação do SIGIC (`colony/`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Incorporar a Fase 4 (SIGIC) ao monorepo como o pacote `aurora_siger/colony/`, refatorado para domínio puro e com continuidade real: o grafo da colônia usa os 13 módulos da Fase 3 como nós.

**Architecture:** Novo domínio `colony/` espelhando `landing/`/`operations/`. `roster.py` deriva os nós de `operations.MODULES` (nome/tipo/consumo) + árvore de criticidade (prioridade); `topology.py` adiciona o overlay de rede (posições, capacidades, necessidade de comunicação, arestas ponderadas). Algoritmos (`search`, `paths`, `analysis`) e modelagem (`modeling`) são puros e retornam dados; `cli.py` concentra todo o I/O e traduz rótulos para PT.

**Tech Stack:** Python 3.11+, stdlib pura (`math`, `heapq`, `collections`, `dataclasses`), `pytest`. Sem dependências novas.

## Global Constraints

- Python ≥ 3.11; **stdlib pura** no domínio `colony/` (sem numpy/pandas/sklearn).
- **Nomes/docstrings em inglês** no pacote; **rótulos em português apenas no `cli.py`**.
- **Type hints obrigatórios** em parâmetros e retornos públicos.
- O domínio é **puro**: nenhuma função fora de `cli.py` chama `print()`/`input()`.
- `colony/` **só lê** `aurora_siger.operations`; **nunca** modifica a Fase 3 (protege 276 testes).
- Testes: `tests/test_colony_<arquivo>.py`; TDD (teste falha antes da implementação).
- Versão sobe para `0.4.0` em `aurora_siger/__init__.py` e `pyproject.toml`.
- Ids dos módulos são `int` 1–13 (vêm de `operations.MODULES`).
- Não tocar na entrega standalone `~/projects/fiap-aurora-siger-fase4` (referência de porte, em leitura).

## Tabela de referência — topologia dos 13 nós (revisar antes de codar)

**Derivados da Fase 3** (`operations.MODULES` + `build_criticality_tree`):

| id | name (EN) | type | consumption (adequate) | tier | priority |
|----|-----------|------|-----:|------|-----:|
| 1 | Command and Control | consumer | 8 | Vital | 10 |
| 2 | Life Support (ECLSS) | consumer | 12 | Vital | 10 |
| 3 | Habitat | consumer | 15 | Vital | 10 |
| 4 | Solar Power | solar_generator | 1 | Sustenance | 7 |
| 5 | Nuclear Power | nuclear_generator | 3 | Sustenance | 7 |
| 6 | Communications | consumer | 5 | Sustenance | 7 |
| 7 | Medical Support | consumer | 6 | Vital | 10 |
| 8 | Food Production | consumer | 10 | Sustenance | 7 |
| 9 | Logistics and Storage | consumer | 4 | Expansion | 4 |
| 10 | ISRU (Local Resources) | consumer | 8 | Sustenance | 7 |
| 11 | Workshop and Maintenance | consumer | 3 | Expansion | 4 |
| 12 | Science Lab | consumer | 5 | Expansion | 4 |
| 13 | Wind Power | wind_generator | 0.5 | Sustenance | 7 |

> **Regra de prioridade (derivável, sem tuning):** `Vital → 10`, `Sustenance → 7`, `Expansion → 4`. Função pura do tier de criticidade; três níveis bastam para o Dijkstra com restrição (ex.: `min_priority=8` → só Vital; `min_priority=5` → Vital+Sustenance).

**Overlay de rede** (`topology.py`, atributos que a Fase 3 não tem):

| id | position (x,y) | storage capacity (kWh) | communication_need (1–10) |
|----|-----|-----:|-----:|
| 1 | (3,3) | 15 | 10 |
| 2 | (2,4) | 20 | 4 |
| 3 | (3,4) | 30 | 5 |
| 4 | (0,4) | 10 | 2 |
| 5 | (0,2) | 15 | 2 |
| 6 | (4,2) | 5 | 10 |
| 7 | (2,3) | 8 | 7 |
| 8 | (1,1) | 20 | 6 |
| 9 | (1,5) | 500 | 4 |
| 10 | (0,1) | 40 | 5 |
| 11 | (1,3) | 5 | 4 |
| 12 | (4,4) | 10 | 8 |
| 13 | (0,0) | 5 | 2 |

**Arestas** (não-direcionadas; `(id1, id2, weight, type)`), 20 no total:

```
(5,1,2,"energy"), (5,2,2,"energy"), (5,3,3,"energy"),
(4,3,2,"energy"), (4,8,2,"energy"), (4,9,2,"energy"),
(5,9,2,"energy"), (13,9,3,"energy"),
(2,3,1,"life"),   (3,7,1,"life"),   (2,7,2,"life"),
(1,6,2,"data"),   (1,12,3,"data"),  (1,3,2,"data"),  (6,7,3,"data"),
(8,10,2,"energy"),(10,11,2,"data"), (11,9,2,"energy"),
(12,8,2,"data"),  (11,5,3,"energy")
```

**Propriedades garantidas (viram teste):** grafo **conexo**; **Wind Power (#13) é folha** → **Logistics and Storage (#9) é ponto de articulação** (remoção isola #13) — caso positivo real de detecção. Geração instalada = `100 + 80 + 30 = 210 kW`. Consumo total (adequate) = `80.5 kW`.

---

### Task 1: Pacote `colony/` + `Module` + `InfrastructureGraph`

**Files:**
- Create: `aurora_siger/colony/__init__.py`
- Create: `aurora_siger/colony/graph.py`
- Test: `tests/test_colony_graph.py`

**Interfaces:**
- Produces: `colony.graph.Module` (`@dataclass`: `id:int, name:str, type:str, consumption:float, priority:int, capacity:float, communication_need:int, position:tuple[float,float]|None=None, status:str="active"`); `colony.graph.InfrastructureGraph` with `add_module(m)`, `add_connection(id1,id2,weight,connection_type="energy")`, `get_neighbors(id)->list[int]`, `get_weight(id1,id2)->float`, `get_module(id)->Module|None`, `module_list:list[Module]`, `modules:dict[int,Module]`, `adjacency_list:dict[int,list[int]]`, `edge_weights:dict[str,float]`, `connection_types:dict[str,str]`, `get_module_count()->int`, `get_connection_count()->int`, `get_adjacency_matrix()->list[list[float]]`, `get_distance_matrix()->list[list[float]]`, `_get_edge_key(id1,id2)->str`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_graph.py
from aurora_siger.colony.graph import Module, InfrastructureGraph


def _tiny_graph():
    g = InfrastructureGraph()
    g.add_module(Module(1, "A", "consumer", 10.0, 5, 100.0, 5, (0, 0)))
    g.add_module(Module(2, "B", "consumer", 20.0, 5, 100.0, 5, (1, 0)))
    g.add_module(Module(3, "C", "consumer", 30.0, 5, 100.0, 5, (2, 0)))
    g.add_connection(1, 2, 2, "energy")
    g.add_connection(2, 3, 4, "data")
    return g


def test_counts_and_neighbors():
    g = _tiny_graph()
    assert g.get_module_count() == 3
    assert g.get_connection_count() == 2
    assert sorted(g.get_neighbors(2)) == [1, 3]


def test_weight_is_symmetric_and_self_zero():
    g = _tiny_graph()
    assert g.get_weight(1, 2) == g.get_weight(2, 1) == 2
    assert g.get_weight(1, 1) == 0


def test_missing_edge_is_infinite():
    g = _tiny_graph()
    assert g.get_weight(1, 3) == float("inf")


def test_matrix_matches_list():
    g = _tiny_graph()
    matrix = g.get_adjacency_matrix()
    # index order follows module_list insertion order: [1,2,3]
    assert matrix[0][1] == 2  # 1-2
    assert matrix[1][2] == 4  # 2-3
    assert matrix[0][2] == 0  # no edge 1-3


def test_duplicate_module_raises():
    g = _tiny_graph()
    import pytest
    with pytest.raises(ValueError):
        g.add_module(Module(1, "dup", "consumer", 1.0, 1, 1.0, 1, None))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/projects/FIAP-Aurora-Siger && pytest tests/test_colony_graph.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony'`

- [ ] **Step 3: Write minimal implementation**

```python
# aurora_siger/colony/__init__.py
"""Fase 4 — topologia da colônia: a infraestrutura como grafo ponderado."""
```

```python
# aurora_siger/colony/graph.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_colony_graph.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
cd ~/projects/FIAP-Aurora-Siger
git add aurora_siger/colony/__init__.py aurora_siger/colony/graph.py tests/test_colony_graph.py
git commit -m "feat(fase-4): colony graph — Module + InfrastructureGraph (puro)"
```

---

### Task 2: `roster.py` — nós derivados da Fase 3

**Files:**
- Create: `aurora_siger/colony/roster.py`
- Test: `tests/test_colony_roster.py`

**Interfaces:**
- Consumes: `aurora_siger.operations.modules.MODULES`, `aurora_siger.operations.hierarchies.build_criticality_tree`.
- Produces: `PRIORITY_BY_TIER:dict[str,int]`; `criticality_of(module_id:int)->str`; `priority_of(module_id:int)->int`; `generation_capacity_kw()->float`; `adequate_consumption(module:dict)->float`; `derived_attributes(module_id:int)->dict` returning `{"id","name","type","consumption","priority"}`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_roster.py
from aurora_siger.colony import roster


def test_priority_from_criticality_tier():
    assert roster.criticality_of(3) == "Vital"          # Habitat
    assert roster.criticality_of(8) == "Sustenance"     # Food Production
    assert roster.criticality_of(12) == "Expansion"     # Science Lab
    assert roster.priority_of(3) == 10
    assert roster.priority_of(8) == 7
    assert roster.priority_of(12) == 4


def test_generation_capacity_is_sum_of_generators():
    # Solar 100 + Nuclear 80 + Wind 30
    assert roster.generation_capacity_kw() == 210.0


def test_derived_attributes_use_adequate_mode():
    attrs = roster.derived_attributes(3)  # Habitat
    assert attrs["name"] == "Habitat"
    assert attrs["type"] == "consumer"
    assert attrs["consumption"] == 15      # adequate mode
    assert attrs["priority"] == 10


def test_all_thirteen_have_a_tier():
    for mid in range(1, 14):
        assert roster.criticality_of(mid) in ("Vital", "Sustenance", "Expansion")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_roster.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.roster'`

- [ ] **Step 3: Write minimal implementation**

```python
# aurora_siger/colony/roster.py
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
```

> **Verified:** `operations.tree.Node` exposes `.name`, `.children` (list) and `.module` (dict|None) — see `aurora_siger/operations/tree.py:14-23`. In `build_criticality_tree` the tier nodes (Vital/Sustenance/Expansion) hold leaf children whose `.module` is the dict, so the two-level walk in `_criticality_index()` is correct. Do not modify `tree.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_colony_roster.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/colony/roster.py tests/test_colony_roster.py
git commit -m "feat(fase-4): roster — nós do grafo derivados da Fase 3 (criticidade→prioridade)"
```

---

### Task 3: `topology.py` — overlay de rede + `build_graph()`

**Files:**
- Create: `aurora_siger/colony/topology.py`
- Test: `tests/test_colony_topology.py`

**Interfaces:**
- Consumes: `colony.graph.Module/InfrastructureGraph`, `colony.roster.derived_attributes`.
- Produces: `POSITIONS:dict[int,tuple]`, `STORAGE_CAPACITY:dict[int,float]`, `COMM_NEED:dict[int,int]`, `EDGES:list[tuple[int,int,float,str]]`; `build_graph()->InfrastructureGraph` (the canonical 13-node colony graph).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_topology.py
from aurora_siger.colony import topology, search


def test_graph_has_thirteen_connected_nodes():
    g = topology.build_graph()
    assert g.get_module_count() == 13
    assert g.get_connection_count() == 20
    components = search.connected_components(g)
    assert len(components) == 1  # fully connected


def test_node_attributes_are_assembled():
    g = topology.build_graph()
    habitat = g.get_module(3)
    assert habitat.name == "Habitat"
    assert habitat.consumption == 15
    assert habitat.priority == 10
    assert habitat.capacity == 30
    assert habitat.communication_need == 5
    assert habitat.position == (3, 4)


def test_edges_are_symmetric():
    g = topology.build_graph()
    for id1, id2, weight, _type in topology.EDGES:
        assert g.get_weight(id1, id2) == weight
        assert g.get_weight(id2, id1) == weight


def test_wind_is_a_leaf():
    g = topology.build_graph()
    assert g.get_neighbors(13) == [9]  # only Logistics
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_topology.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.topology'`
(Note: this test also imports `search`, created in Task 4. Run after Task 4, or temporarily comment the `connected_components` assertion. Cleaner: implement Task 3 and Task 4 back-to-back, committing each. The first run here verifies the topology import fails first.)

- [ ] **Step 3: Write minimal implementation**

```python
# aurora_siger/colony/topology.py
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
```

- [ ] **Step 4: Run test to verify it passes** (after Task 4's `search.py` exists)

Run: `pytest tests/test_colony_topology.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/colony/topology.py tests/test_colony_topology.py
git commit -m "feat(fase-4): topology — overlay de rede + grafo canônico de 13 nós"
```

---

### Task 4: `search.py` — BFS, DFS, componentes (puros)

**Files:**
- Create: `aurora_siger/colony/search.py`
- Test: `tests/test_colony_search.py`

**Interfaces:**
- Consumes: `colony.graph.InfrastructureGraph`.
- Produces: `BFSResult(@dataclass: levels:dict[int,int], paths:dict[int,list[int]], order_by_level:list[list[int]], target_found_at:int|None)`; `DFSResult(@dataclass: order:list[int], path:list[int])`; `bfs(graph,start,target=None)->BFSResult`; `dfs(graph,start,target=None)->DFSResult`; `connected_components(graph)->list[list[int]]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_search.py
from aurora_siger.colony.graph import Module, InfrastructureGraph
from aurora_siger.colony import search


def _line_graph():
    # 1 - 2 - 3 - 4
    g = InfrastructureGraph()
    for i in range(1, 5):
        g.add_module(Module(i, f"M{i}", "consumer", 1.0, 5, 1.0, 1, None))
    g.add_connection(1, 2, 1)
    g.add_connection(2, 3, 1)
    g.add_connection(3, 4, 1)
    return g


def test_bfs_levels():
    res = search.bfs(_line_graph(), 1)
    assert res.levels == {1: 0, 2: 1, 3: 2, 4: 3}
    assert res.paths[4] == [1, 2, 3, 4]


def test_bfs_target_found_level():
    res = search.bfs(_line_graph(), 1, target=3)
    assert res.target_found_at == 2


def test_dfs_reaches_target():
    res = search.dfs(_line_graph(), 1, target=4)
    assert res.path == [1, 2, 3, 4]
    assert res.order[0] == 1


def test_connected_components_counts_islands():
    g = _line_graph()
    g.add_module(Module(99, "island", "consumer", 1.0, 5, 1.0, 1, None))
    comps = search.connected_components(g)
    assert len(comps) == 2
    assert [99] in comps
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_search.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.search'`

- [ ] **Step 3: Write minimal implementation**

```python
# aurora_siger/colony/search.py
"""Graph traversal: BFS by levels, DFS, connected components. Pure — returns data."""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from aurora_siger.colony.graph import InfrastructureGraph


@dataclass
class BFSResult:
    levels: dict[int, int]
    paths: dict[int, list[int]]
    order_by_level: list[list[int]]
    target_found_at: Optional[int] = None


@dataclass
class DFSResult:
    order: list[int] = field(default_factory=list)
    path: list[int] = field(default_factory=list)


def bfs(graph: InfrastructureGraph, start: int,
        target: Optional[int] = None) -> BFSResult:
    if start not in graph.modules:
        return BFSResult({}, {}, [])
    visited = {start}
    queue = deque([start])
    levels = {start: 0}
    paths = {start: [start]}
    order_by_level: list[list[int]] = []
    found_at: Optional[int] = None
    level = 1
    while queue:
        current_level: list[int] = []
        for _ in range(len(queue)):
            current = queue.popleft()
            for neighbor in graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    levels[neighbor] = level
                    paths[neighbor] = paths[current] + [neighbor]
                    current_level.append(neighbor)
                    if target is not None and neighbor == target and found_at is None:
                        found_at = level
        if current_level:
            order_by_level.append(current_level)
        level += 1
    return BFSResult(levels, paths, order_by_level, found_at)


def dfs(graph: InfrastructureGraph, start: int,
        target: Optional[int] = None) -> DFSResult:
    order: list[int] = []

    def walk(node: int, visited: set[int], path: list[int]) -> Optional[list[int]]:
        visited.add(node)
        order.append(node)
        path.append(node)
        if target is not None and node == target:
            return list(path)
        for neighbor in graph.get_neighbors(node):
            if neighbor not in visited:
                found = walk(neighbor, visited, path)
                if found is not None:
                    return found
        path.pop()
        return None

    if start not in graph.modules:
        return DFSResult()
    found = walk(start, set(), [])
    return DFSResult(order=order, path=found or [])


def connected_components(graph: InfrastructureGraph) -> list[list[int]]:
    unvisited = set(graph.modules.keys())
    components: list[list[int]] = []
    while unvisited:
        start = unvisited.pop()
        component: list[int] = []
        queue = deque([start])
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in graph.get_neighbors(current):
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_colony_search.py tests/test_colony_topology.py -q`
Expected: PASS (Task 3's topology tests now pass too)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/colony/search.py tests/test_colony_search.py
git commit -m "feat(fase-4): search — BFS/DFS/componentes puros (retornam dados)"
```

---

### Task 5: `paths.py` — Dijkstra puro + teste de paridade

**Files:**
- Create: `aurora_siger/colony/paths.py`
- Test: `tests/test_colony_paths.py`
- Test: `tests/test_colony_parity.py`

**Interfaces:**
- Consumes: `colony.graph.InfrastructureGraph`.
- Produces: `PathResult(@dataclass: path:list[int], distance:float, steps:list[tuple[int,float]]=[], skipped:list[int]=[])`; `shortest_path(graph,origin,destination)->PathResult`; `shortest_path_with_priority(graph,origin,destination,min_priority)->PathResult`; `all_shortest_paths(graph,origin)->dict[int,PathResult]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_paths.py
from aurora_siger.colony.graph import Module, InfrastructureGraph
from aurora_siger.colony import paths


def _diamond():
    # 1 -2- 2 -2- 4   and   1 -1- 3 -1- 4  (lower route wins: 1-3-4 = 2)
    g = InfrastructureGraph()
    for i, prio in [(1, 9), (2, 3), (3, 9), (4, 9)]:
        g.add_module(Module(i, f"M{i}", "consumer", 1.0, prio, 1.0, 1, None))
    g.add_connection(1, 2, 2)
    g.add_connection(2, 4, 2)
    g.add_connection(1, 3, 1)
    g.add_connection(3, 4, 1)
    return g


def test_shortest_path_picks_cheapest_route():
    res = paths.shortest_path(_diamond(), 1, 4)
    assert res.path == [1, 3, 4]
    assert res.distance == 2
    assert res.steps[0] == (1, 0)        # trace starts at origin, distance 0


def test_priority_constraint_avoids_low_priority_node():
    # min_priority 8 forbids node 2 (prio 3); only route is 1-3-4
    res = paths.shortest_path_with_priority(_diamond(), 1, 4, min_priority=8)
    assert res.path == [1, 3, 4]
    assert 2 in res.skipped


def test_all_shortest_paths_excludes_origin():
    res = paths.all_shortest_paths(_diamond(), 1)
    assert set(res.keys()) == {2, 3, 4}
    assert res[4].distance == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_paths.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.paths'`

- [ ] **Step 3: Write minimal implementation**

```python
# aurora_siger/colony/paths.py
"""Dijkstra shortest paths over the colony graph. Pure — returns data, no I/O.

The step-by-step trace is returned as data (PathResult.steps) so the CLI can
render it; the algorithm itself never prints.
"""

import heapq
from dataclasses import dataclass, field

from aurora_siger.colony.graph import InfrastructureGraph


@dataclass
class PathResult:
    path: list[int]
    distance: float
    steps: list[tuple[int, float]] = field(default_factory=list)
    skipped: list[int] = field(default_factory=list)


def _dijkstra(graph: InfrastructureGraph, origin: int, destination: int,
              min_priority: int | None = None) -> PathResult:
    if origin not in graph.modules or destination not in graph.modules:
        return PathResult([], float("inf"))
    if origin == destination:
        return PathResult([origin], 0.0, steps=[(origin, 0.0)])

    distances = {m: float("inf") for m in graph.modules}
    distances[origin] = 0
    previous: dict[int, int | None] = {origin: None}
    heap: list[tuple[float, int]] = [(0, origin)]
    visited: set[int] = set()
    steps: list[tuple[int, float]] = []
    skipped: list[int] = []

    while heap:
        current_dist, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        steps.append((current, current_dist))
        if current == destination:
            break
        for neighbor in graph.get_neighbors(current):
            if neighbor in visited:
                continue
            if min_priority is not None and graph.modules[neighbor].priority < min_priority:
                if neighbor not in skipped:
                    skipped.append(neighbor)
                continue
            weight = graph.get_weight(current, neighbor)
            if weight == float("inf"):
                continue
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    if distances[destination] == float("inf"):
        return PathResult([], float("inf"), steps=steps, skipped=skipped)
    path: list[int] = []
    node: int | None = destination
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()
    return PathResult(path, distances[destination], steps=steps, skipped=skipped)


def shortest_path(graph: InfrastructureGraph, origin: int, destination: int) -> PathResult:
    return _dijkstra(graph, origin, destination)


def shortest_path_with_priority(graph: InfrastructureGraph, origin: int,
                                destination: int, min_priority: int) -> PathResult:
    if graph.modules.get(origin) and graph.modules[origin].priority < min_priority:
        return PathResult([], float("inf"), skipped=[origin])
    if graph.modules.get(destination) and graph.modules[destination].priority < min_priority:
        return PathResult([], float("inf"), skipped=[destination])
    return _dijkstra(graph, origin, destination, min_priority=min_priority)


def all_shortest_paths(graph: InfrastructureGraph, origin: int) -> dict[int, PathResult]:
    results: dict[int, PathResult] = {}
    for destination in graph.modules:
        if destination == origin:
            continue
        res = shortest_path(graph, origin, destination)
        if res.path:
            results[destination] = res
    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_colony_paths.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Write the parity test (proves the refactor preserved delivered behavior)**

```python
# tests/test_colony_parity.py
"""Regression: the refactored pure algorithms reproduce the standalone Fase 4
delivery's documented outputs, on a fixture rebuilding the original 10-node PT
topology. Data evolved to 13 nodes; algorithm SEMANTICS must not have changed.
Source of expected values: standalone README (Dijkstra ARM->MED = 4.0; BFS from
Centro de Controle). Original ids are strings here only as labels via int proxies.
"""

from aurora_siger.colony.graph import Module, InfrastructureGraph
from aurora_siger.colony import paths, search

# Original 10 modules (id proxy -> name), priorities from data_modules.py.
_ORIG = {
    1: ("Habitacao", 9), 2: ("Centro de Controle", 10), 3: ("Armazenamento de Energia", 8),
    4: ("Producao de Oxigenio", 10), 5: ("Suporte Medico", 9), 6: ("Comunicacao", 8),
    7: ("Agricultura", 7), 8: ("Laboratorio Cientifico", 6), 9: ("Centro de Recreacao", 4),
    10: ("Oficina de Manutencao", 5),
}
# Original connections (proxy ids), weights from DEFAULT_CONNECTIONS.
_CONN = [
    (1, 2, 2), (1, 5, 1), (1, 3, 3), (2, 3, 2), (2, 6, 2), (2, 8, 3),
    (3, 4, 3), (3, 7, 2), (5, 4, 2), (1, 7, 4), (7, 8, 2), (7, 4, 3),
    (8, 6, 3), (6, 5, 3), (2, 5, 3), (9, 8, 2), (9, 6, 3), (10, 3, 2),
    (10, 7, 3), (10, 4, 2),
]


def _original_graph():
    g = InfrastructureGraph()
    for pid, (name, prio) in _ORIG.items():
        g.add_module(Module(pid, name, "consumer", 1.0, prio, 1.0, 1, None))
    for a, b, w in _CONN:
        g.add_connection(a, b, w)
    return g


def test_dijkstra_storage_to_medical_is_four():
    # README: Armazenamento de Energia (3) -> Suporte Medico (5) = 4.0
    # via Armazenamento -> Habitacao -> Suporte Medico (3 + 1)
    res = paths.shortest_path(_original_graph(), 3, 5)
    names = [_ORIG[i][0] for i in res.path]
    assert names == ["Armazenamento de Energia", "Habitacao", "Suporte Medico"]
    assert res.distance == 4.0


def test_bfs_first_level_from_control_centre():
    # README BFS from Centro de Controle (2): level 1 are its direct neighbours.
    res = search.bfs(_original_graph(), 2)
    level1 = set(res.order_by_level[0])
    assert level1 == {1, 3, 6, 8, 5}  # Habitacao, Armazenamento, Comunicacao, Lab, Medico
```

- [ ] **Step 6: Run parity test**

Run: `pytest tests/test_colony_parity.py -q`
Expected: PASS (2 passed). If `test_bfs_first_level_from_control_centre` fails, re-read the standalone README BFS example and adjust the expected set to match the delivered output exactly (do not change the algorithm).

- [ ] **Step 7: Commit**

```bash
git add aurora_siger/colony/paths.py tests/test_colony_paths.py tests/test_colony_parity.py
git commit -m "feat(fase-4): paths — Dijkstra puro (trace como dado) + teste de paridade"
```

---

### Task 6: `analysis.py` — eficiência, articulação (Tarjan), centralidade (Brandes)

**Files:**
- Create: `aurora_siger/colony/analysis.py`
- Test: `tests/test_colony_analysis.py`

**Interfaces:**
- Consumes: `colony.graph.InfrastructureGraph`.
- Produces: `articulation_points(graph)->list[int]`; `clustering_coefficient(graph)->float`; `betweenness(graph)->dict[int,float]` (Brandes, unweighted shortest paths, normalized); `analyze_centrality(graph)->dict[int,dict]` (`{"name","degree","betweenness","priority"}`); `analyze_efficiency(graph)->dict`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_analysis.py
from aurora_siger.colony.graph import Module, InfrastructureGraph
from aurora_siger.colony import analysis, topology


def _bridge():
    # Two triangles A(1,2,3) and B(4,5,6) joined only by edge 3-4.
    g = InfrastructureGraph()
    for i in range(1, 7):
        g.add_module(Module(i, f"N{i}", "consumer", 1.0, 5, 1.0, 1, None))
    for a, b in [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4), (3, 4)]:
        g.add_connection(a, b, 1)
    return g


def test_articulation_points_on_bridge():
    pts = set(analysis.articulation_points(_bridge()))
    assert {3, 4} <= pts          # the two bridge endpoints are cut vertices


def test_real_network_logistics_is_articulation():
    g = topology.build_graph()
    assert 9 in analysis.articulation_points(g)   # Wind(13) hangs off Logistics(9)


def test_clustering_in_unit_interval():
    c = analysis.clustering_coefficient(_bridge())
    assert 0.0 <= c <= 1.0


def test_betweenness_bridge_endpoints_highest():
    bc = analysis.betweenness(_bridge())
    # Bridge endpoints sit on every cross-triangle shortest path → top scores.
    assert bc[3] > bc[1]
    assert bc[4] > bc[6]


def test_efficiency_reports_expected_keys():
    eff = analysis.analyze_efficiency(topology.build_graph())
    for key in ("total_modules", "total_connections", "average_degree",
                "articulation_points", "clustering_coefficient", "overall_status"):
        assert key in eff
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_analysis.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.analysis'`

- [ ] **Step 3: Write minimal implementation**

```python
# aurora_siger/colony/analysis.py
"""Network analysis: articulation points (Tarjan), clustering, betweenness
(Brandes), centrality and an efficiency summary. Pure — returns data."""

from collections import deque

from aurora_siger.colony.graph import InfrastructureGraph


def articulation_points(graph: InfrastructureGraph) -> list[int]:
    """Tarjan's DFS for cut vertices (iterative over roots, recursive within)."""
    visited: set[int] = set()
    disc: dict[int, int] = {}
    low: dict[int, int] = {}
    parent: dict[int, int | None] = {}
    cut: set[int] = set()
    timer = [0]

    def dfs(u: int) -> None:
        visited.add(u)
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        children = 0
        for v in graph.get_neighbors(u):
            if v not in visited:
                children += 1
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent.get(u) is None and children > 1:
                    cut.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    cut.add(u)
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for node in graph.modules:
        if node not in visited:
            parent[node] = None
            dfs(node)
    return sorted(cut)


def clustering_coefficient(graph: InfrastructureGraph) -> float:
    total = 0.0
    counted = 0
    for module in graph.module_list:
        neighbors = graph.get_neighbors(module.id)
        k = len(neighbors)
        if k < 2:
            continue
        links = 0
        for i in range(k):
            for j in range(i + 1, k):
                if neighbors[j] in graph.get_neighbors(neighbors[i]):
                    links += 1
        total += links / (k * (k - 1) / 2)
        counted += 1
    return total / counted if counted else 0.0


def betweenness(graph: InfrastructureGraph) -> dict[int, float]:
    """Brandes betweenness over unweighted shortest paths, normalized to [0,1]."""
    nodes = list(graph.modules.keys())
    cb = {v: 0.0 for v in nodes}
    for s in nodes:
        stack: list[int] = []
        preds: dict[int, list[int]] = {v: [] for v in nodes}
        sigma = {v: 0.0 for v in nodes}
        sigma[s] = 1.0
        dist = {v: -1 for v in nodes}
        dist[s] = 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in graph.get_neighbors(v):
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    preds[w].append(v)
        delta = {v: 0.0 for v in nodes}
        while stack:
            w = stack.pop()
            for v in preds[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                cb[w] += delta[w]
    # Undirected: each pair counted twice. Normalize by (n-1)(n-2).
    n = len(nodes)
    scale = ((n - 1) * (n - 2)) if n > 2 else 1
    return {v: (cb[v] / 2) / scale for v in nodes}


def analyze_centrality(graph: InfrastructureGraph) -> dict[int, dict]:
    bc = betweenness(graph)
    return {
        m.id: {
            "name": m.name,
            "degree": len(graph.get_neighbors(m.id)),
            "betweenness": bc[m.id],
            "priority": m.priority,
        }
        for m in graph.module_list
    }


def analyze_efficiency(graph: InfrastructureGraph) -> dict:
    n = graph.get_module_count()
    edges = graph.get_connection_count()
    average_degree = (2 * edges) / n if n else 0
    communication_efficiency = min(1.0, average_degree / 4.0)
    avg_consumption = (sum(m.consumption for m in graph.module_list) / n) if n else 0
    energy_efficiency = max(0.0, 1.0 - (avg_consumption / 100.0))
    critical_modules = [
        m.name for m in graph.module_list
        if m.priority >= 8 and len(graph.get_neighbors(m.id)) <= 2
    ]
    arts = [graph.modules[a].name for a in articulation_points(graph)]
    weights = list(graph.edge_weights.values())
    status = (
        "otimo" if communication_efficiency > 0.7 and energy_efficiency > 0.7
        else "bom" if communication_efficiency > 0.5 and energy_efficiency > 0.5
        else "critico"
    )
    return {
        "total_modules": n,
        "total_connections": edges,
        "average_degree": average_degree,
        "communication_efficiency": communication_efficiency,
        "energy_efficiency": energy_efficiency,
        "critical_modules": critical_modules,
        "articulation_points": arts,
        "clustering_coefficient": clustering_coefficient(graph),
        "avg_edge_weight": (sum(weights) / len(weights)) if weights else 0,
        "max_edge_weight": max(weights) if weights else 0,
        "min_edge_weight": min(weights) if weights else 0,
        "overall_status": status,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_colony_analysis.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/colony/analysis.py tests/test_colony_analysis.py
git commit -m "feat(fase-4): analysis — Tarjan + Brandes + eficiência (sem caminhos simples exponenciais)"
```

---

### Task 7: `modeling.py` — modelagem matemática ancorada (210 kW)

**Files:**
- Create: `aurora_siger/colony/modeling.py`
- Test: `tests/test_colony_modeling.py`

**Interfaces:**
- Consumes: `colony.graph.InfrastructureGraph`, `colony.roster.generation_capacity_kw`.
- Produces: class `MathematicalModeling(graph)` with `total_consumption(t,growth_rate=0.12)->float`, `consumption_derivative(t,growth_rate=0.12)->float`, `consumption_second_derivative(...)->float`, `energy_loss_by_distance(distance,transmission_efficiency=0.95)->float`, `predict_critical_point(t_max=50)->dict`, `simulate_scenarios()->dict`, `growth_prediction(years=10)->dict`, `temporal_consumption_analysis(years=10,points=100)->dict`, `distribution_efficiency(module_id)->dict`, `cost_benefit_analysis()->dict`. No I/O.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_modeling.py
import math
from aurora_siger.colony import topology
from aurora_siger.colony.modeling import MathematicalModeling


def _model():
    return MathematicalModeling(topology.build_graph())


def test_generation_capacity_is_real_210():
    assert _model().generation_capacity == 210.0


def test_initial_consumption_is_805():
    m = _model()
    assert round(m.total_consumption(0), 1) == 80.5


def test_exponential_growth():
    m = _model()
    c0 = m.total_consumption(0)
    assert math.isclose(m.total_consumption(1), c0 * math.exp(0.12), rel_tol=1e-6)


def test_derivative_matches_analytic():
    m = _model()
    # d/dt C0 e^{rt} = r * C(t)
    t = 3.0
    assert math.isclose(m.consumption_derivative(t),
                        0.12 * m.total_consumption(t), rel_tol=1e-3)


def test_energy_loss_grows_with_distance():
    m = _model()
    assert m.energy_loss_by_distance(1) < m.energy_loss_by_distance(5)


def test_critical_point_around_seven_years():
    m = _model()
    crit = m.predict_critical_point(t_max=50)
    assert crit["critical_year"] is not None
    assert 6.0 <= (crit["critical_year"] - 2026) <= 8.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_modeling.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.modeling'`

- [ ] **Step 3: Write minimal implementation**

Port `modeling/math.py` from the standalone (`~/projects/fiap-aurora-siger-fase4/modeling/math.py`) into `aurora_siger/colony/modeling.py` with these exact changes:
1. Imports: `from aurora_siger.colony.roster import generation_capacity_kw` (drop `from data.data_modules import GENERATION_CAPACITY`).
2. In `__init__`: `self.generation_capacity = generation_capacity_kw()` (= 210.0).
3. Remove the `complete_analysis()` method entirely (its prints move to the CLI; its sub-results are already exposed by the individual methods).
4. Keep all pure methods verbatim (they already return dicts/floats): `total_consumption`, `consumption_per_module`, `consumption_derivative`, `consumption_second_derivative`, `consumption_rate_analysis`, `_interpret_rate_of_change`, `optimal_consumption_point` and its helpers, `operational_cost_function`, `marginal_cost`, `marginal_efficiency`, `temporal_consumption_analysis` and its helpers, `optimize_energy_distribution`, `predict_critical_point`, `simulate_scenarios`, `_analyze_scenario`, `energy_loss_by_distance`, `distribution_efficiency`, `growth_prediction`, `cost_benefit_analysis`.
5. Add type hints to any public signature missing them; translate any inline Portuguese in docstrings only if trivial (leave the PT interpretation strings returned by `_interpret_rate_of_change`/`_generate_recommendations` as-is — they are user-facing copy rendered by the CLI).

Minimal skeleton (the head + the methods exercised by the tests — port the rest verbatim per the steps above):

```python
# aurora_siger/colony/modeling.py
"""Mathematical modeling of colony phenomena (differential calculus).

Anchored to Fase 3: initial consumption is the sum of the 13 modules' adequate
mode; the capacity ceiling is the colony's real installed generation (210 kW),
read from the roster — not a hard-coded constant. Pure: no I/O.
"""

import math

from aurora_siger.colony.graph import InfrastructureGraph
from aurora_siger.colony.roster import generation_capacity_kw


class MathematicalModeling:
    def __init__(self, graph: InfrastructureGraph) -> None:
        self.graph = graph
        self.h = 0.001
        self.generation_capacity = generation_capacity_kw()

    def total_consumption(self, t: float, growth_rate: float = 0.12) -> float:
        c0 = sum(m.consumption for m in self.graph.module_list)
        return c0 * math.exp(growth_rate * t)

    def consumption_derivative(self, t: float, growth_rate: float = 0.12) -> float:
        return (self.total_consumption(t + self.h, growth_rate)
                - self.total_consumption(t - self.h, growth_rate)) / (2 * self.h)

    def consumption_second_derivative(self, t: float, growth_rate: float = 0.12) -> float:
        return (self.total_consumption(t + self.h, growth_rate)
                - 2 * self.total_consumption(t, growth_rate)
                + self.total_consumption(t - self.h, growth_rate)) / (self.h ** 2)

    def energy_loss_by_distance(self, distance: float,
                                transmission_efficiency: float = 0.95) -> float:
        return 1 - math.exp(-distance * (1 - transmission_efficiency))

    def predict_critical_point(self, t_max: int = 50) -> dict:
        cap = self.generation_capacity
        t = 0.0
        while t < t_max:
            consumption = self.total_consumption(t)
            if consumption >= cap * 0.9:
                return {
                    "critical_year": 2026 + t,
                    "consumption": consumption,
                    "capacity": cap,
                    "percentage": (consumption / cap) * 100,
                    "alert_level": "Alto" if consumption / cap > 0.95 else "Medio",
                }
            t += 0.5
        return {"critical_year": None,
                "message": f"Nao atingira capacidade critica nos proximos {t_max} anos."}

    # ... PORT the remaining methods listed in Step 3 verbatim from the standalone,
    #     swapping only the capacity source (self.generation_capacity) and dropping
    #     complete_analysis(). See ~/projects/fiap-aurora-siger-fase4/modeling/math.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_colony_modeling.py -q`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/colony/modeling.py tests/test_colony_modeling.py
git commit -m "feat(fase-4): modeling — cálculo diferencial ancorado na geração real (210 kW)"
```

---

### Task 8: `cli.py` — menu SIGIC (PT na apresentação) + entrypoint

**Files:**
- Create: `aurora_siger/colony/cli.py`
- Modify: `pyproject.toml` (`[project.scripts]`, `authors`, `version`)
- Modify: `aurora_siger/__init__.py` (`__version__`)
- Test: `tests/test_colony_cli.py`

**Interfaces:**
- Consumes: every `colony.*` module above.
- Produces: `PT_LABELS:dict[int,str]`; `label(module)->str`; `main()->None` (entrypoint `sigic`); helper renderers that consume the pure results and `print`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_colony_cli.py
from aurora_siger.colony import cli, topology


def test_pt_labels_cover_all_thirteen():
    g = topology.build_graph()
    for module in g.module_list:
        assert module.id in cli.PT_LABELS
        assert cli.PT_LABELS[module.id]            # non-empty PT name


def test_label_renders_pt_for_known_module():
    g = topology.build_graph()
    assert cli.label(g.get_module(1)) == "Centro de Controle"


def test_main_is_callable():
    assert callable(cli.main)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_colony_cli.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.colony.cli'`

- [ ] **Step 3: Write the CLI**

Port `ui/menu.py` from the standalone into `aurora_siger/colony/cli.py`. The CLI is the ONLY place that prints/reads. Structure to reproduce (port each screen from the standalone, swapping the data source to the pure functions and every module name to `label(module)`):

Head + dispatch + helpers (write this verbatim):

```python
# aurora_siger/colony/cli.py
"""SIGIC terminal UI — the only I/O layer of the colony domain.

Module names are English in the domain; this layer renders Portuguese labels via
PT_LABELS. Every screen consumes the pure results from colony.{search,paths,
analysis,modeling,topology} and prints them.
"""

from aurora_siger.colony import analysis, paths, search, topology
from aurora_siger.colony.graph import Module, InfrastructureGraph
from aurora_siger.colony.modeling import MathematicalModeling

PT_LABELS: dict[int, str] = {
    1: "Centro de Controle",
    2: "Suporte de Vida (ECLSS)",
    3: "Habitacao",
    4: "Energia Solar",
    5: "Energia Nuclear",
    6: "Comunicacoes",
    7: "Suporte Medico",
    8: "Producao de Alimentos",
    9: "Logistica e Armazenamento",
    10: "ISRU (Recursos Locais)",
    11: "Oficina e Manutencao",
    12: "Laboratorio Cientifico",
    13: "Energia Eolica",
}

TYPE_LABELS_PT = {"energy": "energia", "data": "dados", "life": "suporte a vida"}


def label(module: Module) -> str:
    """Portuguese display name for a module (falls back to its EN name)."""
    return PT_LABELS.get(module.id, module.name)


def _select_module(graph: InfrastructureGraph, prompt: str) -> int | None:
    print("\nModulos disponiveis:")
    for i, module in enumerate(graph.module_list, 1):
        print(f"  {i:2d}. {label(module)}")
    try:
        choice = int(input(f"\n{prompt} (numero): ")) - 1
    except ValueError:
        print("\n[ERRO] Entrada invalida!")
        return None
    if 0 <= choice < len(graph.module_list):
        return graph.module_list[choice].id
    print("\n[ERRO] Opcao invalida!")
    return None
```

Screens to port (each is a method/function rendering a pure result; reference the standalone `ui/menu.py` line ranges for the exact print layout, adapting names via `label()`):

| CLI screen | Pure source it calls | Standalone reference |
|---|---|---|
| Visualizar rede | `graph.module_list`, `graph.adjacency_list`, `graph.connection_types` | `_menu_view_network` (111–149) |
| Consultar módulo | `MathematicalModeling.distribution_efficiency` | `_menu_query_module`/`_display_module_details` (175–281) |
| BFS | `search.bfs(...).order_by_level`, `.levels` | `_execute_bfs` (352–371) |
| DFS | `search.dfs(...).path` | `_execute_dfs` (373–397) |
| Dijkstra | `paths.shortest_path(...)` (`.path`,`.distance`,`.steps`) | `_execute_dijkstra` (399–424) |
| Dijkstra c/ restrição | `paths.shortest_path_with_priority(...)` (`.skipped`) | `_execute_dijkstra_constraints` (426–460) |
| Dijkstra todos | `paths.all_shortest_paths(...)` | `_execute_dijkstra_all` (462–490) |
| Eficiência | `analysis.analyze_efficiency(...)` | `_analyze_efficiency` (492–533) |
| Pontos críticos | `analysis.articulation_points(...)` + demo bridge | `_detect_critical_points` (535–590) |
| Centralidade | `analysis.analyze_centrality(...)` | `_analyze_centrality` (618–650) |
| Componentes | `search.connected_components(...)` | `_list_components` (652–681) |
| Modelagem (8 telas) | `MathematicalModeling.*` | `_menu_modeling` block (685–969) |
| Sustentabilidade/ESG | consumo/capacidade somados + texto ESG | `_menu_sustainability` (973–1008) |
| Simulações (4) | `MathematicalModeling.*`, `analysis.articulation_points` | `_menu_simulations` block (1012–1180) |
| Matriz de adjacência | `graph.get_adjacency_matrix()` | `_menu_adjacency_matrix` (1269–1281) |

Also port `_build_demo_bridge_graph` (standalone 592–616) into the CLI (it is presentation: a didactic positive case), adapting `Module(...)` to the new dataclass signature `Module(id, name, type, consumption, priority, capacity, communication_need, position, status)`. End with:

```python
def main() -> None:
    """Entry point for the `sigic` console script."""
    graph = topology.build_graph()
    # ... main while-loop dispatching to the screens above (port _run/run, 36–107) ...
```

> The Dijkstra step-by-step trace is now `result.steps` (list of `(id, distance)`); render it where the standalone printed inside the algorithm (`* {name} (distancia: ...)`).

- [ ] **Step 4: Wire the entrypoint, version and 4th author**

Edit `pyproject.toml`:
- `version = "0.4.0"`
- under `[project.scripts]` add: `sigic = "aurora_siger.colony.cli:main"`
- add to `authors`: `{ name = "Maria Sophia Domingues dos Santos", email = "maria.sophia.domingues@gmail.com" }`
- add keywords: `"graphs"`, `"dijkstra"`, `"bfs"`, `"network-analysis"`

Edit `aurora_siger/__init__.py`: `__version__ = "0.4.0"`.

- [ ] **Step 5: Run tests + a headless import smoke**

Run: `pip install -e ".[dev]" -q && pytest tests/test_colony_cli.py -q`
Expected: PASS (3 passed)

Run: `python -c "from aurora_siger.colony import cli; cli.topology.build_graph()"`
Expected: no output, exit 0 (imports resolve).

- [ ] **Step 6: Commit**

```bash
git add aurora_siger/colony/cli.py tests/test_colony_cli.py pyproject.toml aurora_siger/__init__.py
git commit -m "feat(fase-4): cli SIGIC (PT na apresentacao) + entrypoint sigic + bump 0.4.0"
```

---

### Task 9: `fases/fase-4/` — wrapper, enunciado, figuras, README

**Files:**
- Create: `fases/fase-4/sigic.py`
- Create: `fases/fase-4/enunciado.md` (copy of `~/projects/fiap-aurora-siger-fase4/enunciado.md`)
- Create: `fases/fase-4/figuras/gerar_rede.py`
- Create: `fases/fase-4/figuras/rede_colonia.dot` (generated)
- Create: `fases/fase-4/figuras/rede_colonia.pdf` (generated)
- Create: `fases/fase-4/README.md`

**Interfaces:**
- Consumes: `aurora_siger.colony.cli:main`, `aurora_siger.colony.topology`, `colony.cli.PT_LABELS`.

- [ ] **Step 1: Write the wrapper**

```python
# fases/fase-4/sigic.py
"""Fase 4 entrypoint — thin wrapper over aurora_siger.colony.cli:main.

Mirrors fases/fase-2/mgpeb.py and fases/fase-3/aurora_core.py: lets
`python3 fases/fase-4/sigic.py` run the SIGIC terminal app while the logic lives
in the installable package.
"""

from aurora_siger.colony.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the Graphviz diagram generator**

```python
# fases/fase-4/figuras/gerar_rede.py
"""Regenerates the colony network diagram (13 nodes) from the canonical graph.

Requires Graphviz (`dot`). Writes rede_colonia.dot and rede_colonia.pdf next to
this file. Node labels are Portuguese (PT_LABELS); edge colour encodes the type.
"""

import os
import subprocess

from aurora_siger.colony import topology
from aurora_siger.colony.cli import PT_LABELS, TYPE_LABELS_PT

HERE = os.path.dirname(os.path.abspath(__file__))
EDGE_COLOR = {"energy": "orange", "data": "blue", "life": "red"}


def build_dot() -> str:
    g = topology.build_graph()
    lines = ["graph ColoniaAuroraSiger {", '  layout=neato; overlap=false;',
             '  node [shape=box, style=rounded, fontname="Helvetica"];']
    for m in g.module_list:
        x, y = m.position
        lines.append(f'  {m.id} [label="{PT_LABELS[m.id]}\\n(p{m.priority})", pos="{x},{y}!"];')
    seen = set()
    for id1, neigh in g.adjacency_list.items():
        for id2 in neigh:
            key = (min(id1, id2), max(id1, id2))
            if key in seen:
                continue
            seen.add(key)
            ctype = g.connection_types.get(g._get_edge_key(id1, id2), "energy")
            w = g.get_weight(id1, id2)
            lines.append(f'  {id1} -- {id2} [label="{w:g}", color={EDGE_COLOR.get(ctype,"black")}];')
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    dot = build_dot()
    dot_path = os.path.join(HERE, "rede_colonia.dot")
    pdf_path = os.path.join(HERE, "rede_colonia.pdf")
    with open(dot_path, "w") as f:
        f.write(dot)
    subprocess.run(["dot", "-Tpdf", dot_path, "-o", pdf_path], check=True)
    print(f"Diagrama gerado: {pdf_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Generate the diagram**

Run:
```bash
cd ~/projects/FIAP-Aurora-Siger
which dot || sudo apt-get install -y graphviz   # only if missing
python fases/fase-4/figuras/gerar_rede.py
```
Expected: `Diagrama gerado: .../rede_colonia.pdf`; both `.dot` and `.pdf` exist.
Verify the PDF has **13 nodes** and the orange/blue/red edge colours.

- [ ] **Step 4: Copy the enunciado and write the fase README**

Copy: `cp ~/projects/fiap-aurora-siger-fase4/enunciado.md fases/fase-4/enunciado.md`

Write `fases/fase-4/README.md` (PT) covering: the SIGIC overview, how to run (`python3 fases/fase-4/sigic.py` or `sigic` after install), the 13-node continuity with Fase 3, and the menu map. Use `fases/fase-3/README.md` as the structural template.

- [ ] **Step 5: Commit**

```bash
git add fases/fase-4/
git commit -m "feat(fase-4): wrapper sigic + enunciado + gerador/diagrama de rede (13 nos) + README"
```

---

### Task 10: Relatório técnico + ensaio

**Files:**
- Create: `fases/fase-4/relatorio.md`
- Create: `fases/fase-4/relatorio.pdf` (from the .md)
- Create: `docs/fase-4/operacao-a-topologia.md`

- [ ] **Step 1: Write the technical report**

Write `fases/fase-4/relatorio.md` covering the assignment's required sections (enunciado §1.1–1.6 and the grading rubric §3): infrastructure description; graph representation (with the §4.2 edge justification from the spec); algorithms (BFS/DFS/Dijkstra/articulation/centrality); data structures (list+matrix adjacency, dicts, tuples) **and their justification**; mathematical modeling ($C(t)=C_0e^{rt}$, derivatives, optimization, energy loss) anchored at 210 kW with the ~7.1-year critical point; ESG analysis; **and a "Nota de procedência e continuidade"** explaining the consolidation (standalone delivery → monorepo) and the Fase 3 reuse (13 modules, criticality→priority). Use `fases/fase-3/relatorio.md` as the structural template. Embed `figuras/rede_colonia.pdf`.

- [ ] **Step 2: Render the PDF**

Run (mirror the Fase 3 toolchain — pandoc/xelatex):
```bash
cd ~/projects/FIAP-Aurora-Siger/fases/fase-4
pandoc relatorio.md -o relatorio.pdf --pdf-engine=xelatex
```
Expected: `relatorio.pdf` created. If pandoc/xelatex are missing, install or fall back to the toolchain used for `fases/fase-3/relatorio.pdf` (check that file's provenance).

- [ ] **Step 3: Write the essay**

Write `docs/fase-4/operacao-a-topologia.md` — a reflective essay "Da operação à topologia: a colônia que opera agora se mapeia como rede." Connects Fase 3 (energy operation) to Fase 4 (network topology): why the same 13 modules, why criticality becomes priority, what the articulation point on Logistics reveals about resilience.

- [ ] **Step 4: Commit**

```bash
git add fases/fase-4/relatorio.md fases/fase-4/relatorio.pdf docs/fase-4/
git commit -m "docs(fase-4): relatorio tecnico (PDF) + ensaio operacao-a-topologia"
```

---

### Task 11: README raiz + CLAUDE.md + pytest verde ponta-a-ponta

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the root README**

In `README.md`:
1. Architecture tree: add `│   └── colony/   # Fase 4 — topologia/rede da colônia (grafo + algoritmos)`.
2. Add the prose bullet "**Fase 4 — Topologia (rede):** a colônia que opera agora se mapeia como grafo ponderado; BFS/DFS/Dijkstra, pontos de articulação, centralidade e modelagem de consumo." next to the Fase 3 bullet.
3. New section "## Entregáveis da Fase 4" — table mapping 4.1 código (`aurora_siger/colony/` + `fases/fase-4/sigic.py`), 4.2 diagrama (`fases/fase-4/figuras/rede_colonia.pdf`), 4.3 relatório (`fases/fase-4/relatorio.pdf`), enunciado.
4. Roadmap: mark Fase 4 concluída.
5. **Nota de procedência da Fase 4** (mirror the Fase 3 note): standalone team delivery → consolidation by Iúri, 4 authors credited, with explicit continuity (graph uses the 13 Fase 3 modules).
6. Setup block: add `python3 fases/fase-4/sigic.py` / `sigic`.

- [ ] **Step 2: Update CLAUDE.md (its own "Como adicionar uma nova fase" checklist)**

In `CLAUDE.md`:
1. "Projeto" line: "**fases 1, 2, 3 e 4 concluídas** (versão 0.4.0)".
2. Setup block: new test count (run `pytest -q` to get the number) + `python3 fases/fase-4/sigic.py` (ou `sigic`).
3. Architecture tree: add the `colony/` subtree (graph/roster/topology/search/paths/analysis/modeling/cli).
4. New section "## Decisões de design — fase 4" documenting: continuidade via `operations.MODULES` (fonte única, só leitura); prioridade derivada da árvore de criticidade (`Vital→10, Sustenance→7, Expansion→4`); idioma EN-código / PT-CLI (`PT_LABELS`); betweenness Brandes (substitui enumeração de caminhos simples); `GENERATION_CAPACITY` derivado dos geradores reais (210 kW); Wind como folha → Logistics é ponto de articulação real.

- [ ] **Step 3: Full suite green (Fase 3 intacta + Fase 4 nova)**

Run: `cd ~/projects/FIAP-Aurora-Siger && pytest -q`
Expected: all pass — the 276 Fase 3 tests **unchanged** + the new `test_colony_*` tests. If any Fase 3 test changed status, STOP: `colony/` must only read `operations/`; find what was mutated.

- [ ] **Step 4: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs(fase-4): README (entregaveis+roadmap+procedencia) + CLAUDE.md (decisoes fase 4)"
```

---

## Self-Review (preenchido)

**1. Cobertura do spec:**
- §3 estrutura `colony/` → Tasks 1–8. ✅
- §4 reconciliação (roster/criticidade/210 kW/EN-PT) → Tasks 2, 3, 8. ✅
- §5 algoritmos puros + Brandes → Tasks 4, 5, 6. ✅
- §6 modelagem ancorada → Task 7. ✅
- §7 testes (incl. paridade) → Tasks 1–8 (paridade na 5). ✅
- §8 docs/README/procedência/4ª autora → Tasks 8, 9, 10, 11. ✅
- §11 sequência → Tasks 1–11. ✅

**2. Placeholders:** O único "porte verbatim" guiado é a Task 7 (modeling) e a Task 8 (telas da CLI), ambos com a fonte exata (`~/projects/fiap-aurora-siger-fase4/...`), as mudanças pontuais enumeradas e tabela de referência tela→função→linhas. Não há "TODO/TBD/handle edge cases" soltos.

**3. Consistência de tipos:** `Module(id,name,type,consumption,priority,capacity,communication_need,position,status)` usado igual em graph/topology/parity/cli. `PathResult`/`BFSResult`/`DFSResult` definidos na Task que os produz e consumidos com os mesmos campos. `generation_capacity_kw()` (roster) → `MathematicalModeling.generation_capacity` (Task 7). Ids `int` em todo o pipeline.

## Notas de execução

- Ordem com dependência cruzada: **Task 3 e Task 4 andam juntas** (o teste da topologia usa `search.connected_components`). Implementar 3, depois 4, e rodar os dois testes no fim da 4.
- Rodar `pip install -e ".[dev]"` uma vez antes da Task 8 (entrypoint) — ou no começo, é idempotente.
- Cada Task termina verde e com commit próprio; nenhuma Task modifica `aurora_siger/operations/`.
