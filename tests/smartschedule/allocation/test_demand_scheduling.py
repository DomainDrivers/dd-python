from typing import Final
from unittest.mock import Mock

import pytest

from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.events_publisher import EventsPublisher
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.allocation.in_memory_project_allocations_repository import (
    InMemoryProjectAllocationsRepository,
)


@pytest.fixture()
def allocation_facade() -> AllocationFacade:
    return AllocationFacade(
        project_allocations_repository=InMemoryProjectAllocationsRepository(),
        availability_facade=Mock(spec_set=AvailabilityFacade),
        capability_finder=Mock(CapabilityFinder),
        event_publisher=Mock(spec_set=EventsPublisher),
    )


class TestDemandScheduling:
    JAVA: Final = Demand(
        Capability.skill("JAVA"), TimeSlot.create_daily_time_slot_at_utc(2022, 2, 2)
    )

    def test_schedule_project_demands(
        self, allocation_facade: AllocationFacade
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        demands = Demands.of(self.JAVA)

        allocation_facade.schedule_project_allocations_demands(project_id, demands)

        summary = allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0
        assert summary.demands[project_id].all == [self.JAVA]
