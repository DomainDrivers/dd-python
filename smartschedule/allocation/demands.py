from __future__ import annotations

from dataclasses import dataclass

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demand import Demand
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class Demands:
    all: list[Demand]

    @staticmethod
    def none() -> Demands:
        return Demands(all=[])

    @staticmethod
    def of(*demands: Demand) -> Demands:
        return Demands(all=list(demands))

    @staticmethod
    def all_in_same_time_slot(
        time_slot: TimeSlot, *capabilities: Capability
    ) -> Demands:
        return Demands.of(
            *[Demand(capability, time_slot) for capability in capabilities]
        )

    def with_new(self, new_demands: Demands) -> Demands:
        self.all.extend(new_demands.all)
        return Demands(all=self.all[:])

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
            allocation.capability.can_perform(demand.capability)
            and demand.time_slot.within(allocation.time_slot)
            for allocation in allocations.all
        )
