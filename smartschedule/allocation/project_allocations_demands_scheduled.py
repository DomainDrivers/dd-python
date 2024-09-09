from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.private_event import PrivateEvent


@dataclass(frozen=True)
class ProjectAllocationsDemandsScheduled(PrivateEvent):
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime
    uuid: UUID = field(default_factory=uuid4)
