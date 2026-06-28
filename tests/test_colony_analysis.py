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
