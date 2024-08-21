from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestCreatingNewProject:
    def test_allocate_capability_to_project(
        self, allocation_facade: AllocationFacade
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        java_skill = Capability.skill("JAVA")
        demand = Demand(java_skill, one_day)
        allocatable_resource_id = ResourceId.new_one()
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(
            project_id, Demands.of(demand)
        )

        event = allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, java_skill, one_day
        )

        assert event is not None
        summary = allocation_facade.find_projects_allocations_by_ids(project_id)
        summary.project_allocations[project_id].all == {
            AllocatedCapability(allocatable_resource_id.id, java_skill, one_day)
        }
        summary.demands[project_id].all == [demand]

    def test_can_release_capability_from_project(
        self, allocation_facade: AllocationFacade
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocatable_resource_id = ResourceId.new_one()
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(
            project_id, Demands.none()
        )
        chosen_capability = Capability.skill("JAVA")
        allocate_id = allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, chosen_capability, one_day
        )
        assert allocate_id is not None

        result = allocation_facade.release_from_project(
            project_id, allocate_id, one_day
        )

        assert result is True
        summary = allocation_facade.find_projects_allocations_by_ids(project_id)
        assert len(summary.project_allocations[project_id].all) == 0
