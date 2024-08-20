from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class ProjectAllocationScheduled:
    project_id: ProjectAllocationsId
    from_to: TimeSlot
    occurred_at: datetime
    uuid: UUID = field(default_factory=uuid4)
