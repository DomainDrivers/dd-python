from dataclasses import dataclass, field
from uuid import UUID, uuid4

from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class AllocatedCapability:
    resource_id: UUID
    capability: Capability
    time_slot: TimeSlot
    allocated_capability_id: UUID = field(default_factory=uuid4, compare=False)
