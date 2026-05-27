from aurora_siger.operations.tree import Node


def _toy_tree():
    root = Node("root")
    a = root.add_child(Node("A"))
    a.add_child(Node("leaf-1", module={"id": 1}))
    a.add_child(Node("leaf-2", module={"id": 2}))
    root.add_child(Node("leaf-3", module={"id": 3}))
    return root


def test_leaves_returns_module_dicts():
    leaves = _toy_tree().leaves()
    assert sorted(m["id"] for m in leaves) == [1, 2, 3]


def test_find_by_name():
    assert _toy_tree().find("A").name == "A"
    assert _toy_tree().find("nope") is None


def test_aggregate_sum_over_leaves():
    total = _toy_tree().aggregate(lambda m: m["id"], 0, lambda x, y: x + y)
    assert total == 6


def test_depth():
    assert _toy_tree().depth() == 3
