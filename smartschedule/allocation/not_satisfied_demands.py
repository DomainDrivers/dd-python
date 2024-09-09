from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.published_event import PublishedEvent


@dataclass(frozen=True)
class NotSatisfiedDemands(PublishedEvent):
    missing_demands: dict[ProjectAllocationsId, Demands]
    occurred_at: datetime
    uuid: UUID = field(default_factory=uuid4)

    @classmethod
    def for_one_project(
        cls,
        project_id: ProjectAllocationsId,
        scheduled_demands: Demands,
        occurred_at: datetime,
    ) -> Self:
        return cls({project_id: scheduled_demands}, occurred_at)

    @classmethod
    def all_satisfied(
        cls, project_id: ProjectAllocationsId, occurred_at: datetime
    ) -> Self:
        return cls({project_id: Demands.none()}, occurred_at)
