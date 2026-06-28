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
