from __future__ import annotations

from dataclasses import dataclass

from smartschedule.planning.demand import Demand


@dataclass(frozen=True)
class Demands:
    all: list[Demand]

    @staticmethod
    def none() -> Demands:
        return Demands([])

    @staticmethod
    def of(*demands: Demand) -> Demands:
        return Demands(list(demands))

    def __add__(self, other: Demands) -> Demands:
        return Demands(self.all + other.all)
