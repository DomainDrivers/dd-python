from __future__ import annotations
from dataclasses import dataclass, field

from smartschedule.planning.parallelization.stage import Stage
from smartschedule.sorter.nodes import Nodes


@dataclass
class Node:
    name: str
    content: Stage
    dependencies: Nodes = field(default_factory=lambda: Nodes(set()))

    def depends_on(self, node: Node) -> Node:
        return Node(
            name=self.name,
            content=self.content,
            dependencies=self.dependencies.add(node),
        )

    def __str__(self) -> str:
        return self.name

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return self.name == value.name

    def __hash__(self) -> int:
        return hash(self.name)
