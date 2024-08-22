from datetime import datetime, timezone
from uuid import UUID

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.allocation.projects_allocations_summary import (
    ProjectsAllocationsSummary,
)
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class AllocationFacade:
    def __init__(
        self, project_allocations_repository: ProjectAllocationsRepository
    ) -> None:
        self._project_allocations_repository = project_allocations_repository

    def create_allocation(
        self, time_slot: TimeSlot, scheduled_demands: Demands
    ) -> ProjectAllocationsId:
        project_id = ProjectAllocationsId.new_one()
        project_allocations = ProjectAllocations(
            project_id, Allocations.none(), scheduled_demands, time_slot
        )
        self._project_allocations_repository.add(project_allocations)
        return project_id

    def find_projects_allocations_by_ids(
        self, *project_ids: ProjectAllocationsId
    ) -> ProjectsAllocationsSummary:
        projects_allocations = self._project_allocations_repository.get_all(
            ids=list(project_ids)
        )
        return ProjectsAllocationsSummary.of(*projects_allocations)

    def find_all_projects_allocations(self) -> ProjectsAllocationsSummary:
        projects_allocations = self._project_allocations_repository.get_all()
        return ProjectsAllocationsSummary.of(*projects_allocations)

    def allocate_to_project(
        self,
        project_id: ProjectAllocationsId,
        resource_id: ResourceId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> UUID | None:
        allocations = self._project_allocations_repository.get(project_id)
        event = allocations.allocate(
            resource_id, capability, time_slot, datetime.now(tz=timezone.utc)
        )
        return event.allocated_capability_id if event is not None else None

    def release_from_project(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: UUID,
        time_slot: TimeSlot,
    ) -> bool:
        allocations = self._project_allocations_repository.get(project_id)
        event = allocations.release(
            allocatable_capability_id, time_slot, datetime.now(tz=timezone.utc)
        )
        return event is not None

    def edit_project_dates(
        self, project_id: ProjectAllocationsId, from_to: TimeSlot
    ) -> None:
        allocations = self._project_allocations_repository.get(project_id)
        allocations.define_slot(from_to, datetime.now(tz=timezone.utc))

    def schedule_project_allocations_demands(
        self, project_id: ProjectAllocationsId, demands: Demands
    ) -> None:
        try:
            allocations = self._project_allocations_repository.get(project_id)
        except self._project_allocations_repository.NotFound:
            allocations = ProjectAllocations.empty(project_id)
        allocations.add_demands(demands, datetime.now(tz=timezone.utc))
        self._project_allocations_repository.add(allocations)
