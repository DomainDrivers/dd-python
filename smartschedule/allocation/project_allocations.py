from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from smartschedule.allocation.capability_released import CapabilityReleased
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
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
        allocatable_capability_id: AllocatableCapabilityId,
        capability: Capability,
        requested_slot: TimeSlot,
        when: datetime,
    ) -> CapabilitiesAllocated | None:
        allocated_capability = AllocatedCapability(
            allocatable_capability_id, capability, requested_slot
        )
        new_allocations = self.allocations.add(allocated_capability)
        if self._nothing_allocated(
            new_allocations
        ) or not self._within_project_time_slot(requested_slot):
            return None
        self.allocations = new_allocations
        return CapabilitiesAllocated(
            allocated_capability_id=allocated_capability.allocated_capability_id.id,
            project_id=self.project_id,
            missing_demands=self.missing_demands(),
            occurred_at=when,
        )

    def _nothing_allocated(self, new_allocations: Allocations) -> bool:
        return new_allocations == self.allocations

    def _within_project_time_slot(self, requested_slot: TimeSlot) -> bool:
        if self.time_slot.is_empty():
            return True
        return requested_slot.within(self.time_slot)

    def release(
        self,
        allocated_capability_id: AllocatableCapabilityId,
        time_slot: TimeSlot,
        when: datetime,
    ) -> CapabilityReleased | None:
        new_allocations = self.allocations.remove(allocated_capability_id, time_slot)
        if new_allocations == self.allocations:
            return None
        self.allocations = new_allocations
        return CapabilityReleased(
            project_id=self.project_id,
            missing_demands=self.missing_demands(),
            occurred_at=when,
        )

    def _nothing_released(self) -> bool:
        return False

    def missing_demands(self) -> Demands:
        return self.demands.missing_demands(self.allocations)

    def has_time_slot(self) -> bool:
        return not self.time_slot.is_empty()

    def define_slot(
        self, time_slot: TimeSlot, when: datetime
    ) -> ProjectAllocationScheduled:
        self.time_slot = time_slot
        return ProjectAllocationScheduled(
            project_id=self.project_id, from_to=time_slot, occurred_at=when
        )

    def add_demands(
        self, demands: Demands, when: datetime
    ) -> ProjectAllocationsDemandsScheduled:
        self.demands = self.demands.with_new(demands)
        return ProjectAllocationsDemandsScheduled(
            project_id=self.project_id,
            missing_demands=self.missing_demands(),
            occurred_at=when,
        )
