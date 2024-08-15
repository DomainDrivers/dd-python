from __future__ import annotations
from dataclasses import dataclass

from smartschedule.sorter.nodes import Nodes


@dataclass
class SortedNodes[T]:
    all: list[Nodes[T]]

    @classmethod
    def empty(cls) -> SortedNodes[T]:
        return cls([])

    def add(self, new_nodes: Nodes[T]) -> SortedNodes[T]:
        return SortedNodes[T](self.all + [new_nodes])

    def __str__(self) -> str:
        return f"SortedNodes: {self.all}"
