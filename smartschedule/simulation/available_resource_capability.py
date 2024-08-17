from dataclasses import dataclass
from uuid import UUID

from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.capability import Capability


@dataclass(frozen=True)
class AvailableResourceCapability(CapacityDimension):
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self.capability == capability
