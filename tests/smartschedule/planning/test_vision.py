from datetime import datetime, timedelta
from typing import Final

import pytest

from smartschedule.planning.demand import Demand
from smartschedule.planning.demands import Demands
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.resource_name import ResourceName
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.schedule.assertions.schedule_assert import (
    ScheduleAssert,
)


class TestVision:
    JAN_1: Final = datetime(2020, 1, 1)
    JAN_1_2: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 2))
    JAN_2_5: Final = TimeSlot(datetime(2020, 1, 2), datetime(2020, 1, 5))
    JAN_2_12: Final = TimeSlot(datetime(2020, 1, 2), datetime(2020, 1, 12))
    RESOURCE_1: Final = ResourceName("r1")
    RESOURCE_2: Final = ResourceName("r2")
    RESOURCE_4: Final = ResourceName("r4")

    @pytest.mark.xfail(reason="Not implemented yet", strict=True)
    def test_vision_validation_process(self, planning_facade: PlanningFacade) -> None:
        project_id = planning_facade.add_new_project("vision")
        java = Demands.of(Demand.for_(Capability.skill("JAVA")))
        planning_facade.add_demands(project_id, java)

        self._verify_possible_risk_during_planning(project_id, java)

        planning_facade.define_project_stages(
            project_id,
            Stage("Stage 1", resources=frozenset({self.RESOURCE_1})),
            Stage("Stage 2", resources=frozenset({self.RESOURCE_2, self.RESOURCE_1})),
            Stage("Stage 3", resources=frozenset({self.RESOURCE_4})),
        )

        project_card = planning_facade.load(project_id)
        assert str(project_card.parallelized_stages) in (
            "Stage 1 | Stage 2, Stage 3",
            "Stage 2, Stage 3 | Stage 1",
        )

        planning_facade.define_project_stages(
            project_id,
            Stage(
                "Stage 1",
                duration=timedelta(days=1),
                resources=frozenset({self.RESOURCE_1}),
            ),
            Stage(
                "Stage 2",
                duration=timedelta(days=3),
                resources=frozenset({self.RESOURCE_2, self.RESOURCE_1}),
            ),
            Stage(
                "Stage 3",
                duration=timedelta(days=10),
                resources=frozenset({self.RESOURCE_4}),
            ),
        )

        planning_facade.define_start_date(project_id, self.JAN_1)

        schedule = planning_facade.load(project_id).schedule
        schedule_assert = ScheduleAssert(schedule)
        schedule_assert.assert_has_stage("Stage 1").assert_with_slot(self.JAN_1_2)
        schedule_assert.assert_has_stage("Stage 2").assert_with_slot(self.JAN_2_5)
        schedule_assert.assert_has_stage("Stage 3").assert_with_slot(self.JAN_2_12)

    def _verify_possible_risk_during_planning(
        self, project_id: ProjectId, demands: Demands
    ) -> None:
        pass
