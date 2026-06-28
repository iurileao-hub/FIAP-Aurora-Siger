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
