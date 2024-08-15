from __future__ import annotations
from dataclasses import dataclass

from smartschedule.sorter.nodes import Nodes


@dataclass
class SortedNodes:
    all: list[Nodes]

    @classmethod
    def empty(cls) -> SortedNodes:
        return cls([])

    def add(self, new_nodes: Nodes) -> SortedNodes:
        return SortedNodes(self.all + [new_nodes])

    def __str__(self) -> str:
        return f"SortedNodes: {self.all}"
