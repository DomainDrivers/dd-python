from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


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

    def assert_availability_is_released(
        self,
        time_slot: TimeSlot,
        allocatable_capability_id: AllocatableCapabilityId,
        project_id: ProjectAllocationsId,
    ) -> None:
        __tracebackhide__ = True

        owner = Owner(project_id.id)
        calendars = self._availability_facade.load_calendars(
            {allocatable_capability_id.to_availability_resource_id()}, time_slot
        )
        assert all(
            calendar.taken_by(owner) == [] for calendar in calendars.calendars.values()
        )
