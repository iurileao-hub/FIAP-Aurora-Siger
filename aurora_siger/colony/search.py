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
    order: list[int] = []

    def walk(node: int, visited: set[int], path: list[int]) -> Optional[list[int]]:
        visited.add(node)
        order.append(node)
        path.append(node)
        if target is not None and node == target:
            return list(path)
        for neighbor in graph.get_neighbors(node):
            if neighbor not in visited:
                found = walk(neighbor, visited, path)
                if found is not None:
                    return found
        path.pop()
        return None

    if start not in graph.modules:
        return DFSResult()
    found = walk(start, set(), [])
    return DFSResult(order=order, path=found or [])


def connected_components(graph: InfrastructureGraph) -> list[list[int]]:
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
    return components
