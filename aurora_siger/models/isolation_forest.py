"""Isolation Forest implementation from scratch for anomaly detection."""

import numpy as np


class IsolationTreeNode:
    """A node in an isolation tree — either internal (split) or leaf (size)."""

    def __init__(
        self,
        feature: int | None = None,
        threshold: float | None = None,
        left: "IsolationTreeNode | None" = None,
        right: "IsolationTreeNode | None" = None,
        size: int | None = None,
    ):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.size = size


class IsolationTree:
    """A single isolation tree that isolates observations via random splits."""

    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.root: IsolationTreeNode | None = None

    def fit(self, X: np.ndarray) -> None:
        """Build the tree from data matrix X."""
        self.root = self._grow_tree(X, depth=0)

    def _grow_tree(self, X: np.ndarray, depth: int) -> IsolationTreeNode:
        n_samples, n_features = X.shape

        if depth >= self.max_depth or n_samples <= 1:
            return IsolationTreeNode(size=n_samples)

        feature = np.random.randint(0, n_features)
        min_val = X[:, feature].min()
        max_val = X[:, feature].max()

        if min_val == max_val:
            return IsolationTreeNode(size=n_samples)

        threshold = np.random.uniform(min_val, max_val)

        left_mask = X[:, feature] < threshold
        right_mask = ~left_mask

        if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
            return IsolationTreeNode(size=n_samples)

        left = self._grow_tree(X[left_mask], depth + 1)
        right = self._grow_tree(X[right_mask], depth + 1)

        return IsolationTreeNode(feature, threshold, left, right)

    def path_length(self, x: np.ndarray) -> float:
        """Compute the path length for a single observation."""
        return self._path_length(x, self.root, 0)

    def _path_length(
        self, x: np.ndarray, node: IsolationTreeNode, depth: int
    ) -> float:
        if node.size is not None:
            return depth + self._average_path_length(node.size)

        if x[node.feature] < node.threshold:
            return self._path_length(x, node.left, depth + 1)
        else:
            return self._path_length(x, node.right, depth + 1)

    @staticmethod
    def _average_path_length(n: int) -> float:
        """Average path length of an unsuccessful BST search (normalization factor).

        Uses the Euler-Mascheroni constant to approximate the harmonic number.
        """
        if n <= 1:
            return 0
        return 2 * (np.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)


class MyIsolationForest:
    """Isolation Forest ensemble for anomaly detection.

    Args:
        n_trees: Number of isolation trees in the ensemble.
        sample_size: Subsample size for each tree.
    """

    def __init__(self, n_trees: int, sample_size: int):
        self.n_trees = n_trees
        self.sample_size = sample_size
        self.trees: list[IsolationTree] = []

    def fit(self, X: np.ndarray) -> None:
        """Fit the forest by building isolation trees on random subsamples."""
        self.trees = []
        n_samples = X.shape[0]
        max_depth = int(np.ceil(np.log2(self.sample_size)))

        for _ in range(self.n_trees):
            idxs = np.random.choice(n_samples, self.sample_size, replace=False)
            sample = X[idxs]
            tree = IsolationTree(max_depth)
            tree.fit(sample)
            self.trees.append(tree)

    def anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """Compute anomaly scores for each row. Higher = more anomalous."""
        scores = []
        c = self._average_path_length(self.sample_size)

        for x in X:
            avg_path = np.mean([tree.path_length(x) for tree in self.trees])
            score = 2 ** (-avg_path / c)
            scores.append(score)

        return np.array(scores)

    def predict(self, X: np.ndarray, contamination: float = 0.03) -> np.ndarray:
        """Predict anomaly labels: -1 for anomaly, 1 for normal."""
        scores = self.anomaly_score(X)
        threshold = np.percentile(scores, 100 * (1 - contamination))
        return np.where(scores >= threshold, -1, 1)

    @staticmethod
    def _average_path_length(n: int) -> float:
        """Average path length of an unsuccessful BST search (normalization factor).

        Intentionally duplicated from IsolationTree to keep each class self-contained.
        """
        if n <= 1:
            return 0
        return 2 * (np.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)
