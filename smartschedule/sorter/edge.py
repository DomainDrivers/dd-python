from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    source: int
    target: int

    def __str__(self) -> str:
        return f"({self.source} -> {self.target})"
