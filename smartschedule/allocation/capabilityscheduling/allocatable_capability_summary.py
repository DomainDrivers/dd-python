from dataclasses import dataclass

from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.shared.capability_selector import (
    CapabilitySelector,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class AllocatableCapabilitySummary:
    id: AllocatableCapabilityId
    allocatable_resource_id: AllocatableResourceId
    capabilities: CapabilitySelector
    time_slot: TimeSlot
