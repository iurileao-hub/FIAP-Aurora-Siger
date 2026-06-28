"""Graph traversal: BFS by levels, DFS, connected components. Pure — returns data."""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from aurora_siger.colony.graph import InfrastructureGraph


@dataclass
class BFSResult:
    levels: dict[int, int]
    paths: dict[int, list[int]]
    order_by_level: list[list[int]]
    target_found_at: Optional[int] = None


@dataclass
class DFSResult:
    order: list[int] = field(default_factory=list)
    path: list[int] = field(default_factory=list)


def bfs(graph: InfrastructureGraph, start: int,
        target: Optional[int] = None) -> BFSResult:
    """Breadth-first traversal by levels. The start node is level 0 (present in
    `levels`/`paths`); `order_by_level` lists discovered nodes from level 1 onward.
    If `target` is given and reachable, returns its level; else `target_found_at` is None."""
    if start not in graph.modules:
        return BFSResult({}, {}, [])
    visited = {start}
    queue = deque([start])
    levels = {start: 0}
    paths = {start: [start]}
    order_by_level: list[list[int]] = []
    found_at: Optional[int] = None
    level = 1
    while queue:
        current_level: list[int] = []
        for _ in range(len(queue)):
            current = queue.popleft()
            for neighbor in graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    levels[neighbor] = level
                    paths[neighbor] = paths[current] + [neighbor]
                    current_level.append(neighbor)
                    if target is not None and neighbor == target and found_at is None:
                        found_at = level
        if current_level:
            order_by_level.append(current_level)
        level += 1
    return BFSResult(levels, paths, order_by_level, found_at)


def dfs(graph: InfrastructureGraph, start: int,
        target: Optional[int] = None) -> DFSResult:
    """Depth-first traversal (iterative). Returns visit order and, if `target`
    is given and reachable, the root-to-target path (else an empty path)."""
    if start not in graph.modules:
        return DFSResult()
    order: list[int] = []
    visited: set[int] = set()
    stack: list[tuple[int, list[int]]] = [(start, [])]
    found_path: list[int] = []
    while stack:
        node, path = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        path = path + [node]
        if target is not None and node == target:
            found_path = path
            break
        for neighbor in reversed(graph.get_neighbors(node)):
            if neighbor not in visited:
                stack.append((neighbor, path))
    return DFSResult(order=order, path=found_path)


def connected_components(graph: InfrastructureGraph) -> list[list[int]]:
    """Find all connected components in the graph. Each component is sorted and
    the list of components is sorted lexicographically for deterministic output."""
    unvisited = set(graph.modules.keys())
    components: list[list[int]] = []
    while unvisited:
        start = unvisited.pop()
        component: list[int] = []
        queue = deque([start])
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in graph.get_neighbors(current):
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components)
