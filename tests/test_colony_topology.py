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
