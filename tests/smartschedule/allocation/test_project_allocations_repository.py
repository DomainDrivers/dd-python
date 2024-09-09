from datetime import datetime

import pytest
from lagom import Container

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def repository(container: Container) -> ProjectAllocationsRepository:
    return container.resolve(ProjectAllocationsRepository)


class TestProjectAllocationsRepository:
    def test_finds_projects_containing_date(
        self, repository: ProjectAllocationsRepository
    ) -> None:
        project_allocations_before = self._project_allocations(
            ProjectAllocationsId.new_one(),
            TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1),
        )
        project_id_within = ProjectAllocationsId.new_one()
        project_allocations_within = self._project_allocations(
            project_id_within,
            TimeSlot.create_daily_time_slot_at_utc(2021, 2, 1),
        )
        project_allocations_after = self._project_allocations(
            ProjectAllocationsId.new_one(),
            TimeSlot.create_daily_time_slot_at_utc(2021, 3, 1),
        )
        repository.add(project_allocations_before)
        repository.add(project_allocations_within)
        repository.add(project_allocations_after)

        result = repository.find_all_containing_date(datetime(2021, 2, 1))

        assert len(result) == 1
        assert result[0].project_id == project_id_within

    def _project_allocations(
        self, project_id: ProjectAllocationsId, time_slot: TimeSlot
    ) -> ProjectAllocations:
        return ProjectAllocations(
            project_id, Allocations.none(), Demands.none(), time_slot
        )
