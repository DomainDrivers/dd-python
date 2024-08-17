from __future__ import annotations

from dataclasses import dataclass

from smartschedule.optimization.weight_dimension import WeightDimension
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)


@dataclass(frozen=True)
class Demand(WeightDimension[AvailableResourceCapability]):
    capability: Capability
    slot: TimeSlot

    @classmethod
    def demand_for(cls, capability: Capability, slot: TimeSlot) -> Demand:
        return Demand(capability, slot)

    def is_satisfied_by(
        self, available_capability: AvailableResourceCapability
    ) -> bool:
        return available_capability.performs(self.capability) and self.slot.within(
            available_capability.time_slot
        )
