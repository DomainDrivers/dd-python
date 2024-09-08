from datetime import datetime, timedelta
from typing import Final

from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.schedule.assertions.schedule_assert import (
    ScheduleAssert,
)


class TestTimeCriticalWaterfall:
    JAN_1_5: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 5))
    JAN_1_3: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 3))
    JAN_1_4: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 4))

    def test_time_critical_waterfall_project_process(
        self, planning_facade: PlanningFacade
    ) -> None:
        project_id = planning_facade.add_new_project("waterfall")
        stage_before_critical = Stage("Stage1", duration=timedelta(days=2))
        critical_stage = Stage("Stage2", duration=self.JAN_1_5.duration)
        stage_after_critical = Stage("Stage3", duration=timedelta(days=3))
        planning_facade.define_project_stages(
            project_id, stage_before_critical, critical_stage, stage_after_critical
        )

        planning_facade.plan_critical_stage(project_id, critical_stage, self.JAN_1_5)

        schedule = planning_facade.load(project_id).schedule
        schedule_assert = ScheduleAssert(schedule)
        schedule_assert.assert_has_stage("Stage1").assert_with_slot(self.JAN_1_3)
        schedule_assert.assert_has_stage("Stage2").assert_with_slot(self.JAN_1_5)
        schedule_assert.assert_has_stage("Stage3").assert_with_slot(self.JAN_1_4)
