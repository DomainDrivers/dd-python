from datetime import datetime
from typing import Final

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.publish_missing_demands_service import (
    CreateHourlyDemandsSummaryService,
)
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestCreateHourlyDemandsSummaryService:
    NOW: Final = datetime.now()
    JAN: Final = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)
    CSHARP: Final = Demands.of(Demand(Capability.skill("CSHARP"), JAN))
    JAVA: Final = Demands.of(Demand(Capability.skill("JAVA"), JAN))

    service = CreateHourlyDemandsSummaryService()

    def test_creates_missing_demands_summary_for_all_given_projects(self) -> None:
        csharp_project_id = ProjectAllocationsId.new_one()
        java_project_id = ProjectAllocationsId.new_one()
        csharp_project = ProjectAllocations(
            csharp_project_id, Allocations.none(), self.CSHARP, self.JAN
        )
        java_project = ProjectAllocations(
            java_project_id, Allocations.none(), self.JAVA, self.JAN
        )

        result = self.service.create([csharp_project, java_project], self.NOW)

        assert result.occurred_at == self.NOW
        expected_missing_demands = {
            java_project_id: self.JAVA,
            csharp_project_id: self.CSHARP,
        }
        assert result.missing_demands == expected_missing_demands

    def test_takes_into_account_only_projects_with_time_slot(self) -> None:
        with_time_slot_id = ProjectAllocationsId.new_one()
        without_time_slot_id = ProjectAllocationsId.new_one()
        with_time_slot = ProjectAllocations(
            with_time_slot_id, Allocations.none(), self.CSHARP, self.JAN
        )
        without_time_slot = ProjectAllocations(
            without_time_slot_id, Allocations.none(), self.CSHARP, TimeSlot.empty()
        )

        result = self.service.create([with_time_slot, without_time_slot], self.NOW)

        assert result.occurred_at == self.NOW
        assert result.missing_demands == {with_time_slot_id: self.CSHARP}
