from __future__ import annotations

from dataclasses import dataclass

from smartschedule.simulation.demand import Demand


@dataclass(frozen=True)
class Demands:
    all: list[Demand]

    @classmethod
    def of(cls, demands: list[Demand]) -> Demands:
        return Demands(all=demands)
