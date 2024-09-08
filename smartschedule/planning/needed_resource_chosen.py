from dataclasses import dataclass
from datetime import datetime

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class NeededResourcesChosen:
    project_id: ProjectId
    needed_resources: set[ResourceId]
    time_slot: TimeSlot
    occurred_at: datetime
