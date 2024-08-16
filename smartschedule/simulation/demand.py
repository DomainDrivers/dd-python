from __future__ import annotations

from dataclasses import dataclass

from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)
from smartschedule.simulation.capability import Capability
from smartschedule.simulation.time_slot import TimeSlot


@dataclass(frozen=True)
class Demand:
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
