from dataclasses import dataclass
from typing import Self
from uuid import UUID

from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import (
    CapabilitySelector,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class AvailableResourceCapability(CapacityDimension):
    resource_id: UUID
    capability_selector: CapabilitySelector
    time_slot: TimeSlot

    @classmethod
    def with_capability(
        cls, resource_id: UUID, capability: Capability, time_slot: TimeSlot
    ) -> Self:
        return cls(
            resource_id, CapabilitySelector.can_just_perform(capability), time_slot
        )

    def performs(self, capability: Capability) -> bool:
        return self.capability_selector.can_perform(capability)
