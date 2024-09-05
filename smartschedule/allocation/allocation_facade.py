from datetime import datetime, timezone
from uuid import UUID

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.allocation.projects_allocations_summary import (
    ProjectsAllocationsSummary,
)
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class AllocationFacade:
    def __init__(
        self,
        project_allocations_repository: ProjectAllocationsRepository,
        availability_facade: AvailabilityFacade,
        capability_finder: CapabilityFinder,
    ) -> None:
        self._project_allocations_repository = project_allocations_repository
        self._availability_facade = availability_facade
        self._capability_finder = capability_finder

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
        allocatable_capability_id: AllocatableCapabilityId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> UUID | None:
        owner = Owner(project_id.id)
        # yes, one transaction crossing 2 modules.
        if not self._capability_finder.is_present(allocatable_capability_id):
            return None
        if (
            self._availability_facade.block(
                allocatable_capability_id.to_availability_resource_id(),
                time_slot,
                owner,
            )
            is False
        ):
            return None

        event = self._allocate(
            project_id, allocatable_capability_id, capability, time_slot
        )
        return event.allocated_capability_id if event is not None else None

    def allocate_capability_to_project_for_period(
        self,
        project_id: ProjectAllocationsId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> bool:
        proposed_capabilities = self._capability_finder.find_capabilities(
            capability, time_slot
        )
        if not proposed_capabilities.all:
            return False

        availability_resource_ids = {
            resource.id.to_availability_resource_id()
            for resource in proposed_capabilities.all
        }
        chosen = self._availability_facade.block_random_available(
            availability_resource_ids, time_slot, Owner(project_id.id)
        )
        if not chosen:
            return False

        to_allocate = self._find_chosen_allocatable_capability(
            proposed_capabilities, chosen
        )
        if not to_allocate:
            return False

        allocated_event = self._allocate(project_id, to_allocate, capability, time_slot)
        return allocated_event is not None

    def _allocate(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        capability: Capability,
        time_slot: TimeSlot,
    ) -> CapabilitiesAllocated | None:
        allocations = self._project_allocations_repository.get(project_id)
        return allocations.allocate(
            allocatable_capability_id,
            capability,
            time_slot,
            datetime.now(tz=timezone.utc),
        )

    def _find_chosen_allocatable_capability(
        self, proposed_capabilities: AllocatableCapabilitiesSummary, chosen: ResourceId
    ) -> AllocatableCapabilityId | None:
        matching = [
            ac.id
            for ac in proposed_capabilities.all
            if ac.id.to_availability_resource_id() == chosen
        ]
        return next(iter(matching), None)

    def release_from_project(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
        time_slot: TimeSlot,
    ) -> bool:
        # can release not scheduled capability - at least for now.
        # Hence no check to CapabilityFinder
        self._availability_facade.release(
            allocatable_capability_id.to_availability_resource_id(),
            time_slot,
            Owner(project_id.id),
        )
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
