from datetime import datetime, timedelta
from typing import Final

import pytest

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.planning.project_card import ProjectCard
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.schedule.assertions.schedule_assert import (
    ScheduleAssert,
)


class TestRd:
    JANUARY: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 31))
    FEBRUARY: Final = TimeSlot(datetime(2020, 2, 1), datetime(2020, 2, 29))
    MARCH: Final = TimeSlot(datetime(2020, 3, 1), datetime(2020, 3, 31))
    Q1: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 3, 31))
    JAN_1_4: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 4))
    FEB_2_16: Final = TimeSlot(datetime(2020, 2, 2), datetime(2020, 2, 16))
    MAR_1_6: Final = TimeSlot(datetime(2020, 3, 1), datetime(2020, 3, 6))

    @pytest.mark.xfail(reason="Not implemented yet", strict=True)
    def test_research_and_development_project_process(
        self, planning_facade: PlanningFacade
    ) -> None:
        project_id = planning_facade.add_new_project("R&D")
        r1 = ResourceId.new_one()
        java_available_in_january = self._resource_available_for_capability_in_period(
            r1, Capability.skill("JAVA"), self.JANUARY
        )
        r2 = ResourceId.new_one()
        php_available_in_february = self._resource_available_for_capability_in_period(
            r2, Capability.skill("PHP"), self.FEBRUARY
        )
        r3 = ResourceId.new_one()
        csharp_available_in_march = self._resource_available_for_capability_in_period(
            r3, Capability.skill("CSHARP"), self.MARCH
        )
        all_resources = {r1, r2, r3}

        planning_facade.define_resources_within_dates(
            project_id, all_resources, self.JANUARY
        )

        self._verify_that_resources_are_missing(
            project_id, {php_available_in_february, csharp_available_in_march}
        )

        planning_facade.define_resources_within_dates(
            project_id, all_resources, self.FEBRUARY
        )

        self._verify_that_resources_are_missing(
            project_id, {java_available_in_january, csharp_available_in_march}
        )

        planning_facade.define_resources_within_dates(
            project_id, all_resources, self.Q1
        )

        self._verify_that_no_resources_are_missing(project_id)

        planning_facade.adjust_stages_to_resource_availability(
            project_id,
            self.Q1,
            Stage("Stage1", duration=timedelta(days=3), resources=frozenset({r1})),
            Stage("Stage1", duration=timedelta(days=15), resources=frozenset({r2})),
            Stage("Stage3", duration=timedelta(days=5), resources=frozenset({r3})),
        )

        loaded = planning_facade.load(project_id)
        schedule_assert = ScheduleAssert(loaded.schedule)
        schedule_assert.assert_has_stage("Stage1").assert_with_slot(self.JAN_1_4)
        schedule_assert.assert_has_stage("Stage2").assert_with_slot(self.FEB_2_16)
        schedule_assert.assert_has_stage("Stage3").assert_with_slot(self.MAR_1_6)
        self._assert_project_is_not_parallelized(loaded)

    def _resource_available_for_capability_in_period(
        self, resource_id: ResourceId, capability: Capability, time_slot: TimeSlot
    ) -> ResourceId:
        # TODO
        return ResourceId.new_one()

    def _assert_project_is_not_parallelized(self, project_card: ProjectCard) -> None:
        __tracebackhide__ = True

        assert (
            len(project_card.parallelized_stages.all) == 0
        ), "Project should not be parallelized"

    def _verify_that_no_resources_are_missing(self, project_id: ProjectId) -> None:
        pass

    def _verify_that_resources_are_missing(
        self, project_id: ProjectId, missing_resources: set[ResourceId]
    ) -> None:
        pass
