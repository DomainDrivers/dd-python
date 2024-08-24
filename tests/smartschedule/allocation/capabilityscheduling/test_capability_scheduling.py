from datetime import timedelta

import pytest
from lagom import Container

from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.allocation.capabilityscheduling.capability_scheduler import (
    CapabilityScheduler,
)
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def capability_scheduler(container: Container) -> CapabilityScheduler:
    return container.resolve(CapabilityScheduler)


@pytest.fixture()
def capability_finder(container: Container) -> CapabilityFinder:
    return container.resolve(CapabilityFinder)


class AvailabilityAssert:
    def __init__(self, availability_facade: AvailabilityFacade) -> None:
        self._facade = availability_facade

    def assert_availability_slots_created(
        self, resource_id: ResourceId, time_slot: TimeSlot
    ) -> None:
        calendar = self._facade.load_calendar(resource_id, time_slot)
        assert calendar.available_slots() == [time_slot]


@pytest.fixture()
def availability_assert(availability_facade: AvailabilityFacade) -> AvailabilityAssert:
    return AvailabilityAssert(availability_facade)


class TestCapabilityScheduling:
    def test_schedule_allocatable_capabilities(
        self,
        capability_scheduler: CapabilityScheduler,
        capability_finder: CapabilityFinder,
        availability_assert: AvailabilityAssert,
    ) -> None:
        java_skill = Capability.skill("JAVA")
        rust_skill = Capability.skill("RUST")
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        allocatable = capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [java_skill, rust_skill], one_day
        )

        loaded = capability_finder.find_by_id(allocatable)
        assert len(allocatable) == len(loaded.all)
        for allocatable_capability_id in allocatable:
            availability_assert.assert_availability_slots_created(
                allocatable_capability_id.to_availability_resource_id(), one_day
            )

    def test_capabililty_is_found_when_capability_present_in_time_slot(
        self,
        capability_scheduler: CapabilityScheduler,
        capability_finder: CapabilityFinder,
    ) -> None:
        unique_skill = Capability.skill("FITNESS-CLASS")
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        another_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 2)
        capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [unique_skill], one_day
        )

        found = capability_finder.find_available_capabilities(unique_skill, one_day)
        not_found = capability_finder.find_available_capabilities(
            unique_skill, another_day
        )

        assert len(found.all) == 1
        assert len(not_found.all) == 0
        assert found.all[0].capability == unique_skill
        assert found.all[0].time_slot == one_day

    def test_capability_not_found_when_capability_not_present(
        self,
        capability_scheduler: CapabilityScheduler,
        capability_finder: CapabilityFinder,
    ) -> None:
        admin = Capability.permission("ADMIN")
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [admin], one_day
        )

        rust = Capability.skill("RUST JUST FOR NINJAS")
        found = capability_finder.find_available_capabilities(rust, one_day)

        assert len(found.all) == 0

    def test_schedule_multiple_capabilities_of_the_same_type(
        self,
        capability_scheduler: CapabilityScheduler,
        capability_finder: CapabilityFinder,
    ) -> None:
        loading = Capability.skill("LOADING_TRUCK")
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        truck1 = AllocatableResourceId.new_one()
        truck2 = AllocatableResourceId.new_one()
        truck3 = AllocatableResourceId.new_one()
        capability_scheduler.schedule_multiple_resources_for_period(
            {truck1, truck2, truck3}, loading, one_day
        )

        found = capability_finder.find_capabilities(loading, one_day)

        assert len(found.all) == 3

    def test_find_capability_ignoring_availability(
        self,
        capability_scheduler: CapabilityScheduler,
        capability_finder: CapabilityFinder,
    ) -> None:
        admin = Capability.permission("ADMIN")
        one_day = TimeSlot.create_daily_time_slot_at_utc(1111, 1, 1)
        different_day = TimeSlot.create_daily_time_slot_at_utc(2021, 2, 1)
        hour_within_day = TimeSlot(one_day.from_, one_day.from_ + timedelta(hours=1))
        partially_overlapping_day = TimeSlot(
            one_day.from_ + timedelta(hours=1), one_day.to + timedelta(hours=1)
        )
        capability_scheduler.schedule_resource_capabilities_for_period(
            AllocatableResourceId.new_one(), [admin], one_day
        )

        on_the_exact_day = capability_finder.find_capabilities(admin, one_day)
        on_different_day = capability_finder.find_capabilities(admin, different_day)
        in_slot_within = capability_finder.find_capabilities(admin, hour_within_day)
        in_overlapping_slot = capability_finder.find_capabilities(
            admin, partially_overlapping_day
        )

        assert len(on_the_exact_day.all) == 1
        assert len(on_different_day.all) == 0
        assert len(in_slot_within.all) == 1
        assert len(in_overlapping_slot.all) == 0
