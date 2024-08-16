from dataclasses import dataclass
from uuid import UUID

from smartschedule.simulation.capability import Capability
from smartschedule.simulation.time_slot import TimeSlot


@dataclass(frozen=True)
class AvailableResourceCapability:
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot

    def performs(self, capability: Capability) -> bool:
        return self.capability == capability
