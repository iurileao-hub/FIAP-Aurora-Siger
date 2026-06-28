"""Dijkstra shortest paths over the colony graph. Pure — returns data, no I/O.

The step-by-step trace is returned as data (PathResult.steps) so the CLI can
render it; the algorithm itself never prints.
"""

import heapq
from dataclasses import dataclass, field

from aurora_siger.colony.graph import InfrastructureGraph


@dataclass
class PathResult:
    path: list[int]
    distance: float
    steps: list[tuple[int, float]] = field(default_factory=list)
    skipped: list[int] = field(default_factory=list)


def _dijkstra(graph: InfrastructureGraph, origin: int, destination: int,
              min_priority: int | None = None) -> PathResult:
    if origin not in graph.modules or destination not in graph.modules:
        return PathResult([], float("inf"))
    if origin == destination:
        return PathResult([origin], 0.0, steps=[(origin, 0.0)])

    distances = {m: float("inf") for m in graph.modules}
    distances[origin] = 0
    previous: dict[int, int | None] = {origin: None}
    heap: list[tuple[float, int]] = [(0, origin)]
    visited: set[int] = set()
    steps: list[tuple[int, float]] = []
    skipped: list[int] = []

    while heap:
        current_dist, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        steps.append((current, current_dist))
        if current == destination:
            break
        for neighbor in graph.get_neighbors(current):
            if neighbor in visited:
                continue
            if min_priority is not None and graph.modules[neighbor].priority < min_priority:
                if neighbor not in skipped:
                    skipped.append(neighbor)
                continue
            weight = graph.get_weight(current, neighbor)
            if weight == float("inf"):
                continue
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    if distances[destination] == float("inf"):
        return PathResult([], float("inf"), steps=steps, skipped=skipped)
    path: list[int] = []
    node: int | None = destination
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()
    return PathResult(path, distances[destination], steps=steps, skipped=skipped)


def shortest_path(graph: InfrastructureGraph, origin: int, destination: int) -> PathResult:
    return _dijkstra(graph, origin, destination)


def shortest_path_with_priority(graph: InfrastructureGraph, origin: int,
                                destination: int, min_priority: int) -> PathResult:
    if graph.modules.get(origin) and graph.modules[origin].priority < min_priority:
        return PathResult([], float("inf"), skipped=[origin])
    if graph.modules.get(destination) and graph.modules[destination].priority < min_priority:
        return PathResult([], float("inf"), skipped=[destination])
    return _dijkstra(graph, origin, destination, min_priority=min_priority)


def all_shortest_paths(graph: InfrastructureGraph, origin: int) -> dict[int, PathResult]:
    results: dict[int, PathResult] = {}
    for destination in graph.modules:
        if destination == origin:
            continue
        res = shortest_path(graph, origin, destination)
        if res.path:
            results[destination] = res
    return results
