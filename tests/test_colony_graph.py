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
