from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from smartschedule.allocation.capability_released import CapabilityReleased
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.sqlalchemy_extensions import AsJSON, EmbeddedUUID, registry
from smartschedule.shared.timeslot.time_slot import TimeSlot


@registry.mapped_as_dataclass()
class ProjectAllocations:
    __tablename__ = "project_allocations"

    project_id: Mapped[ProjectAllocationsId] = mapped_column(
        EmbeddedUUID[ProjectAllocationsId], primary_key=True
    )
    allocations: Mapped[Allocations] = mapped_column(AsJSON[Allocations])
    demands: Mapped[Demands] = mapped_column(AsJSON[Demands])
    time_slot: Mapped[TimeSlot] = mapped_column(AsJSON[TimeSlot])

    def __init__(
        self,
        project_id: ProjectAllocationsId,
        allocations: Allocations,
        demands: Demands,
        time_slot: TimeSlot,
    ) -> None:
        self.project_id = project_id
        self.allocations = allocations
        self.demands = demands
        self.time_slot = time_slot

    @staticmethod
    def empty(project_id: ProjectAllocationsId) -> ProjectAllocations:
        return ProjectAllocations(
            project_id, Allocations.none(), Demands.none(), TimeSlot.empty()
        )

    @staticmethod
    def with_demands(
        project_id: ProjectAllocationsId, demands: Demands
    ) -> ProjectAllocations:
        return ProjectAllocations(
            project_id, Allocations.none(), demands, TimeSlot.empty()
        )

    def allocate(
        self,
        resource_id: ResourceId,
        capability: Capability,
        requested_slot: TimeSlot,
        when: datetime,
    ) -> CapabilitiesAllocated | None:
        if self._nothing_allocated() or not self._within_project_time_slot(
            requested_slot
        ):
            return None
        return None  # return CapabilitiesAllocated(...)

    def _nothing_allocated(self) -> bool:
        return False

    def _within_project_time_slot(self, requested_slot: TimeSlot) -> bool:
        return False

    def release(
        self, allocated_capability_id: UUID, time_slot: TimeSlot, when: datetime
    ) -> CapabilityReleased | None:
        if self._nothing_released():
            return None
        return None  # return CapabilityReleased(...)

    def _nothing_released(self) -> bool:
        return False

    def missing_demands(self) -> Demands:
        return self.demands.missing_demands(self.allocations)

    def has_time_slot(self) -> bool:
        return not self.time_slot.is_empty()
