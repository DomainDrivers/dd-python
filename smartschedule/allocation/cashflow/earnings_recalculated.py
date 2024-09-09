from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.published_event import PublishedEvent


@dataclass(frozen=True)
class EarningsRecalculated(PublishedEvent):
    project_id: ProjectAllocationsId
    earnings: Earnings
    occurred_at: datetime
    uuid: UUID = field(default_factory=uuid4)
