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
