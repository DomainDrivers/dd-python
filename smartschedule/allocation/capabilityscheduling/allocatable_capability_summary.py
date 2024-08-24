from dataclasses import dataclass

from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class AllocatableCapabilitySummary:
    id: AllocatableCapabilityId
    allocatable_resource_id: AllocatableResourceId
    capability: Capability
    time_slot: TimeSlot
