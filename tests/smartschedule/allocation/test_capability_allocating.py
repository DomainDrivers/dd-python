from typing import Callable, TypeAlias

import pytest

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot

AllocatableResourceFactory: TypeAlias = Callable[[TimeSlot], ResourceId]


@pytest.fixture()
def allocatable_resource_factory(
    availability_facade: AvailabilityFacade,
) -> AllocatableResourceFactory:
    def _create_allocatable_resource(period: TimeSlot) -> ResourceId:
        resource_id = ResourceId.new_one()
        availability_facade.create_resource_slots(resource_id, period)
        return resource_id

    return _create_allocatable_resource


class AvailabilityAssert:
    def __init__(self, availability_facade: AvailabilityFacade) -> None:
        self._availability_facade = availability_facade

    def assert_availability_was_blocked(
        self,
        resource_id: ResourceId,
        period: TimeSlot,
        project_id: ProjectAllocationsId,
    ) -> None:
        __tracebackhide__ = True

        owner = Owner(project_id.id)
        calendars = self._availability_facade.load_calendars({resource_id}, period)
        assert all(
            calendar.taken_by(owner) == [period]
            for calendar in calendars.calendars.values()
        )


@pytest.fixture()
def availability_assert(availability_facade: AvailabilityFacade) -> AvailabilityAssert:
    return AvailabilityAssert(availability_facade)


class TestCapabilityAllocating:
    def test_allocate_capability_to_project(
        self,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,
        availability_assert: AvailabilityAssert,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java = Capability.skill("JAVA")
        demand = Demand(skill_java, one_day)
        allocatable_resource_id = allocatable_resource_factory(one_day)
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(
            project_id, Demands.of(demand)
        )

        result = allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, skill_java, one_day
        )

        assert result is not None
        summary = allocation_facade.find_all_projects_allocations()
        assert summary.project_allocations[project_id].all == {
            AllocatedCapability(allocatable_resource_id.id, skill_java, one_day)
        }
        summary.demands[project_id].all == [demand]
        availability_assert.assert_availability_was_blocked(
            allocatable_resource_id, one_day, project_id
        )

    def test_cant_allocate_when_resource_not_available(
        self,
        allocatable_resource_factory: AllocatableResourceFactory,
        availability_facade: AvailabilityFacade,
        allocation_facade: AllocationFacade,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        skill_java = Capability.skill("JAVA")
        demand = Demand(skill_java, one_day)
        allocatable_resource_id = allocatable_resource_factory(one_day)
        availability_facade.block(allocatable_resource_id, one_day, Owner.new_one())
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(
            project_id, Demands.of(demand)
        )

        result = allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, skill_java, one_day
        )

        assert result is None
        summary = allocation_facade.find_all_projects_allocations()
        assert summary.project_allocations[project_id].all == set()

    def test_release_capability_for_the_project(
        self,
        allocation_facade: AllocationFacade,
        allocatable_resource_factory: AllocatableResourceFactory,
    ) -> None:
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocatable_resource_id = allocatable_resource_factory(one_day)
        project_id = ProjectAllocationsId.new_one()
        allocation_facade.schedule_project_allocations_demands(
            project_id, Demands.none()
        )
        chosen_capability = Capability.skill("JAVA")
        allocated_id = allocation_facade.allocate_to_project(
            project_id, allocatable_resource_id, chosen_capability, one_day
        )
        assert allocated_id is not None

        result = allocation_facade.release_from_project(
            project_id, allocated_id, one_day
        )

        assert result is True
        summary = allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0
