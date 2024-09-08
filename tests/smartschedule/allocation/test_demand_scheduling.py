from typing import Any, Final

from mockito import verify  # type: ignore
from mockito.matchers import arg_that  # type: ignore

from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.event_bus import EventBus
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestDemandScheduling:
    JAVA: Final = Demand(
        Capability.skill("JAVA"), TimeSlot.create_daily_time_slot_at_utc(2022, 2, 2)
    )

    def test_schedule_project_demands(
        self, allocation_facade: AllocationFacade, when: Any
    ) -> None:
        when(EventBus).publish(...)
        project_id = ProjectAllocationsId.new_one()
        demands = Demands.of(self.JAVA)

        allocation_facade.schedule_project_allocations_demands(project_id, demands)

        summary = allocation_facade.find_all_projects_allocations()
        assert len(summary.project_allocations[project_id].all) == 0
        assert summary.demands[project_id].all == [self.JAVA]
        verify(EventBus).publish(
            arg_that(
                lambda arg: self._is_project_allocation_event(arg, project_id, demands)
            )
        )

    def _is_project_allocation_event(
        self, event: Any, project_id: ProjectAllocationsId, demands: Demands
    ) -> bool:
        return (
            isinstance(event, ProjectAllocationsDemandsScheduled)
            and event.project_id == project_id
            and event.missing_demands == demands
        )
