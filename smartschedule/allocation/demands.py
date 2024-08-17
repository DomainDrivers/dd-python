from __future__ import annotations

from dataclasses import dataclass

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demand import Demand


@dataclass(frozen=True)
class Demands:
    all: list[Demand]

    def missing_demands(self, allocations: Allocations) -> Demands:
        return Demands(
            [
                demand
                for demand in self.all
                if not self._satisfied_by(demand, allocations)
            ]
        )

    def _satisfied_by(self, demand: Demand, allocations: Allocations) -> bool:
        return any(
            allocation.capability == demand.capability
            and demand.time_slot.within(allocation.time_slot)
            for allocation in allocations.all
        )
