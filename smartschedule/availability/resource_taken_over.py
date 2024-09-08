from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class ResourceTakenOver:
    resource_id: ResourceId
    previous_owners: set[Owner]
    slot: TimeSlot
    occurred_at: datetime
    uuid: UUID = field(default_factory=uuid4)
