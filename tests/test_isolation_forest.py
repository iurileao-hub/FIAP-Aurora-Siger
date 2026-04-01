import numpy as np
from aurora_siger.models.isolation_forest import (
    IsolationTreeNode,
    IsolationTree,
    MyIsolationForest,
)


def test_isolation_tree_node_leaf():
    node = IsolationTreeNode(size=10)
    assert node.size == 10
    assert node.feature is None


def test_isolation_tree_node_internal():
    node = IsolationTreeNode(feature=2, threshold=0.5)
    assert node.feature == 2
    assert node.threshold == 0.5


def test_isolation_tree_fits():
    rng = np.random.RandomState(42)
    X = rng.randn(100, 3)
    tree = IsolationTree(max_depth=8)
    tree.fit(X)
    assert tree.root is not None


def test_isolation_tree_path_length_returns_float():
    rng = np.random.RandomState(42)
    X = rng.randn(100, 3)
    tree = IsolationTree(max_depth=8)
    tree.fit(X)
    length = tree.path_length(X[0])
    assert isinstance(length, float)


def test_average_path_length_base_cases():
    tree = IsolationTree(max_depth=1)
    assert tree._average_path_length(1) == 0
    assert tree._average_path_length(0) == 0


def test_average_path_length_known_value():
    tree = IsolationTree(max_depth=1)
    result = tree._average_path_length(256)
    expected = 2 * (np.log(255) + 0.5772156649) - (2 * 255 / 256)
    assert abs(result - expected) < 1e-6


def test_forest_anomaly_scores_shape():
    rng = np.random.RandomState(42)
    X = rng.randn(200, 3)
    forest = MyIsolationForest(n_trees=10, sample_size=64)
    forest.fit(X)
    scores = forest.anomaly_score(X)
    assert scores.shape == (200,)


def test_forest_outlier_scores_higher():
    rng = np.random.RandomState(42)
    X_normal = rng.randn(200, 2)
    X_outlier = np.array([[10.0, 10.0], [-10.0, -10.0]])
    X = np.vstack([X_normal, X_outlier])

    forest = MyIsolationForest(n_trees=50, sample_size=64)
    forest.fit(X)
    scores = forest.anomaly_score(X)

    normal_mean = scores[:200].mean()
    outlier_mean = scores[200:].mean()
    assert outlier_mean > normal_mean


def test_forest_predict_labels():
    rng = np.random.RandomState(42)
    X = rng.randn(500, 3)
    forest = MyIsolationForest(n_trees=20, sample_size=64)
    forest.fit(X)
    preds = forest.predict(X, contamination=0.05)
    assert set(np.unique(preds)).issubset({-1, 1})
    n_anomalies = np.sum(preds == -1)
    assert 10 <= n_anomalies <= 40  # ~5% of 500
