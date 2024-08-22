from datetime import datetime, timedelta
from typing import Final

import pytest

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.demand import Demand
from smartschedule.planning.demands import Demands
from smartschedule.planning.demands_per_stage import DemandsPerStage
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.schedule.assertions.schedule_assert import (
    ScheduleAssert,
)


class TestStandardWaterfall:
    JAN_1: Final = datetime(2020, 1, 1)
    RESOURCE_1: Final = ResourceId.new_one()
    RESOURCE_2: Final = ResourceId.new_one()
    RESOURCE_4: Final = ResourceId.new_one()
    JAN_1_2: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 2))
    JAN_2_5: Final = TimeSlot(datetime(2020, 1, 2), datetime(2020, 1, 5))
    JAN_2_12: Final = TimeSlot(datetime(2020, 1, 2), datetime(2020, 1, 12))

    @pytest.mark.skip("Not implemented yet")
    def test_waterfall_project_process(self, planning_facade: PlanningFacade) -> None:
        project_id = planning_facade.add_new_project("waterfall")

        planning_facade.define_project_stages(
            project_id, Stage("Stage1"), Stage("Stage2"), Stage("Stage3")
        )

        project_card = planning_facade.load(project_id)
        assert str(project_card.parallelized_stages) == "Stage1, Stage2, Stage3"

        demands_per_stage = DemandsPerStage(
            {"Stage1": Demands.of(Demand.for_(Capability.skill("JAVA")))}
        )
        planning_facade.define_demands_per_stage(project_id, demands_per_stage)

        self._verify_risk_during_planning(project_id)

        planning_facade.define_project_stages(
            project_id,
            Stage(
                "Stage1",
                duration=timedelta(days=1),
                resources=frozenset({self.RESOURCE_1}),
            ),
            Stage(
                "Stage2",
                duration=timedelta(days=3),
                resources=frozenset({self.RESOURCE_2, self.RESOURCE_1}),
            ),
            Stage(
                "Stage3",
                duration=timedelta(days=10),
                resources=frozenset({self.RESOURCE_4}),
            ),
        )
        planning_facade.define_start_date(project_id, self.JAN_1)

        schedule = planning_facade.load(project_id).schedule
        schedule_assert = ScheduleAssert(schedule)
        # schedule_assert.assert_has_stage("Stage1").assert_with_slot(self.JAN_1_2)
        schedule_assert.assert_has_stage("Stage2").assert_with_slot(self.JAN_2_5)
        schedule_assert.assert_has_stage("Stage3").assert_with_slot(self.JAN_2_12)

    def _verify_risk_during_planning(self, project_id: ProjectId) -> None:
        pass
