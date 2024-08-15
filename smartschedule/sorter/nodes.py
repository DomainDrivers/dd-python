from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable


if TYPE_CHECKING:
    from smartschedule.sorter.node import Node


@dataclass
class Nodes:
    nodes: set[Node]

    @property
    def all(self) -> set[Node]:
        return self.nodes.copy()

    def add(self, node: Node) -> Nodes:
        new_nodes = self.nodes.copy()
        new_nodes.add(node)
        return Nodes(new_nodes)

    def with_all_dependencies_present_in(self, nodes: Iterable[Node]) -> Nodes:
        return Nodes(
            {node for node in self.nodes if node.dependencies.nodes.issubset(nodes)}
        )

    def remove_all(self, nodes: set[Node]) -> Nodes:
        return Nodes({node for node in self.nodes if node not in nodes})

    def __str__(self) -> str:
        return f"Nodes{{node={self.nodes}}}"
