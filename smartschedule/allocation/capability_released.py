from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId


@dataclass(frozen=True)
class CapabilityReleased:
    project_id: ProjectAllocationsId
    missing_demands: Demands
    occurred_at: datetime
    event_id: UUID = field(default_factory=uuid4)
