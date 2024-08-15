from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable


if TYPE_CHECKING:
    from smartschedule.sorter.node import Node


@dataclass
class Nodes[T]:
    nodes: set[Node[T]]

    @property
    def all(self) -> set[Node[T]]:
        return self.nodes.copy()

    def add(self, node: Node[T]) -> Nodes[T]:
        new_nodes = self.nodes.copy()
        new_nodes.add(node)
        return Nodes[T](new_nodes)

    def with_all_dependencies_present_in(self, nodes: Iterable[Node[T]]) -> Nodes[T]:
        return Nodes[T](
            {node for node in self.nodes if node.dependencies.nodes.issubset(nodes)}
        )

    def remove_all(self, nodes: set[Node[T]]) -> Nodes[T]:
        return Nodes[T]({node for node in self.nodes if node not in nodes})

    def __str__(self) -> str:
        return f"Nodes{{node={self.nodes}}}"
