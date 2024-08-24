from __future__ import annotations

from smartschedule.sorter.edge import Edge
from smartschedule.sorter.node import Node


class FeedbackArcSeOnGraph[T]:
    def calculate(self, initial_nodes: list[Node[T]]) -> list[Edge]:
        initial_nodes = sorted(initial_nodes, key=lambda node: node.name)
        adjacency_list = self._create_adjacency_list(initial_nodes)
        v = len(adjacency_list)
        feedback_edges = []
        visited = [0] * (v + 1)
        for i in adjacency_list.keys():
            neighbours = adjacency_list[i]
            if len(neighbours) != 0:
                visited[i] = 1
                for j in range(len(neighbours)):
                    if visited[neighbours[j]] == 1:
                        feedback_edges.append(Edge(i, neighbours[j]))
                    else:
                        visited[neighbours[j]] = 1
        return feedback_edges

    def _create_adjacency_list(
        self, initial_nodes: list[Node[T]]
    ) -> dict[int, list[int]]:
        adjacency_list: dict[int, list[int]] = {}

        for i in range(1, len(initial_nodes) + 1):
            adjacency_list[i] = []

        for i in range(len(initial_nodes)):
            dependencies = []
            for dependency in initial_nodes[i].dependencies.nodes:
                dependencies.append(initial_nodes.index(dependency) + 1)
            adjacency_list[i + 1] = dependencies
        return adjacency_list
