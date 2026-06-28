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
