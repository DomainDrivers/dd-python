from typing import Any
from unittest.mock import Mock

import pytest
from mockito import mock, verify  # type: ignore
from mockito.matchers import arg_that  # type: ignore

from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.events_publisher import EventsPublisher
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.allocation.in_memory_project_allocations_repository import (
    InMemoryProjectAllocationsRepository,
)


@pytest.fixture()
def event_publisher() -> Any:
    return mock(EventsPublisher)


@pytest.fixture()
def allocation_facade(event_publisher: Any) -> AllocationFacade:
    return AllocationFacade(
        project_allocations_repository=InMemoryProjectAllocationsRepository(),
        availability_facade=Mock(spec_set=AvailabilityFacade),
        capability_finder=Mock(CapabilityFinder),
        event_publisher=event_publisher,
    )


class TestCreatingNewProject:
    JAN = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
    FEB = TimeSlot.create_monthly_time_slot_at_utc(2021, 2)

    def test_create_new_projct(
        self, allocation_facade: AllocationFacade, event_publisher: Any, when: Any
    ) -> None:
        when(event_publisher).publish(...).thenReturn(None)
        demand = Demand(Capability.skill("JAVA"), self.JAN)

        demands = Demands.of(demand)
        new_project_id = allocation_facade.create_allocation(self.JAN, demands)

        summary = allocation_facade.find_all_projects_allocations()
        assert summary.demands[new_project_id] == demands
        assert summary.time_slots[new_project_id] == self.JAN
        verify(event_publisher).publish(
            arg_that(
                lambda arg: self._is_project_allocation_event(
                    arg, new_project_id, self.JAN
                )
            )
        )

    def test_redefine_project_deadline(
        self,
        allocation_facade: AllocationFacade,
        event_publisher: Any,
        when: Any,
    ) -> None:
        when(event_publisher).publish(...).thenReturn(None)
        demand = Demand(Capability.skill("JAVA"), self.JAN)
        demands = Demands.of(demand)
        new_project_id = allocation_facade.create_allocation(self.JAN, demands)

        allocation_facade.edit_project_dates(new_project_id, self.FEB)

        summary = allocation_facade.find_all_projects_allocations()
        assert summary.time_slots[new_project_id] == self.FEB
        verify(event_publisher).publish(
            arg_that(
                lambda arg: self._is_project_allocation_event(
                    arg, new_project_id, self.FEB
                )
            )
        )

    def _is_project_allocation_event(
        self, event: Any, project_id: ProjectAllocationsId, time_slot: TimeSlot
    ) -> bool:
        return (
            isinstance(event, ProjectAllocationScheduled)
            and event.project_id == project_id
            and event.from_to == time_slot
        )
