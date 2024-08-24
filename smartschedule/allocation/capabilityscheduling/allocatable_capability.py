from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.sqlalchemy_extensions import AsJSON, EmbeddedUUID, registry
from smartschedule.shared.timeslot.time_slot import TimeSlot


@registry.mapped_as_dataclass()
class AllocatableCapability:
    __tablename__ = "allocatable_capabilities"

    id: Mapped[AllocatableCapabilityId] = mapped_column(
        EmbeddedUUID[AllocatableCapabilityId], primary_key=True
    )
    capability: Mapped[Capability] = mapped_column(AsJSON[Capability])
    resource_id: Mapped[AllocatableResourceId] = mapped_column(
        AsJSON[AllocatableResourceId]
    )
    _from_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="from_date"
    )
    _to_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="to_date")

    def __init__(
        self,
        resource_id: AllocatableResourceId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> None:
        self.id = AllocatableCapabilityId.new_one()
        self.resource_id = resource_id
        self.capability = capability
        self._from_date = time_slot.from_
        self._to_date = time_slot.to

    @property
    def time_slot(self) -> TimeSlot:
        return TimeSlot(self._from_date, self._to_date)

    def can_perform(self, capability: Capability) -> bool:
        return self.capability == capability
