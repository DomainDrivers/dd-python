from dataclasses import dataclass

from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.shared.capability_selector import CapabilitySelector
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class AllocatedCapability:
    allocated_capability_id: AllocatableCapabilityId
    capability: CapabilitySelector
    time_slot: TimeSlot
