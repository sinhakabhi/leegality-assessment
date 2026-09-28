import heapq
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

EdgeTuple = tuple[str, str, Decimal]


@dataclass(frozen=True)
class Route:
    total_latency: Decimal
    path: list[str]


def find_shortest_path(edges: Iterable[EdgeTuple], source: str, destination: str) -> Route | None:
    graph: dict[str, list[tuple[str, Decimal]]] = defaultdict(list)
    for edge_source, edge_destination, latency in edges:
        graph[edge_source].append((edge_destination, latency))

    distances: dict[str, Decimal] = {source: Decimal(0)}
    previous: dict[str, str] = {}
    visited: set[str] = set()
    queue: list[tuple[Decimal, str]] = [(Decimal(0), source)]

    while queue:
        distance, node = heapq.heappop(queue)
        if node in visited:
            continue
        if node == destination:
            return Route(total_latency=distance, path=_build_path(previous, destination))
        visited.add(node)

        for neighbour, latency in graph[node]:
            candidate = distance + latency
            if neighbour not in distances or candidate < distances[neighbour]:
                distances[neighbour] = candidate
                previous[neighbour] = node
                heapq.heappush(queue, (candidate, neighbour))

    return None


def _build_path(previous: dict[str, str], destination: str) -> list[str]:
    path = [destination]
    while path[-1] in previous:
        path.append(previous[path[-1]])
    return path[::-1]
