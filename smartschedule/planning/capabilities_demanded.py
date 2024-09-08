from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smartschedule.planning.demands import Demands
from smartschedule.planning.project_id import ProjectId


@dataclass(frozen=True)
class CapabilitiesDemanded:
    project_id: ProjectId
    demands: Demands
    occurred_at: datetime
    uuid: UUID = field(default_factory=uuid4)
