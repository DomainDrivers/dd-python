from dataclasses import dataclass
from datetime import datetime

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class CriticalStagePlanned:
    project_id: ProjectId
    stage_time_slot: TimeSlot
    critical_resource_id: ResourceId | None
    occurred_at: datetime
