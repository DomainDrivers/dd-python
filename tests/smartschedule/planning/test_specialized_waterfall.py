from datetime import datetime, timedelta
from typing import Final

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.resource_name import ResourceName
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.schedule.assertions.schedule_assert import (
    ScheduleAssert,
)


class TestSpecializedWaterfall:
    JAN_1_2: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 2))
    JAN_1_4: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 4))
    JAN_1_5: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 5))
    JAN_1_6: Final = TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 6))
    JAN_4_8: Final = TimeSlot(datetime(2020, 1, 4), datetime(2020, 1, 8))

    def test_specialized_waterfall_project_process(
        self, planning_facade: PlanningFacade
    ) -> None:
        project_id = planning_facade.add_new_project("waterfall")
        critical_stage_duration = timedelta(days=5)
        stage_1_duration = timedelta(days=1)
        stage_before_critical = Stage("Stage 1", duration=stage_1_duration)
        critical_stage = Stage("Stage 2", duration=critical_stage_duration)
        stage_after_critical = Stage("Stage 3", duration=timedelta(days=3))
        planning_facade.define_project_stages(
            project_id, stage_before_critical, critical_stage, stage_after_critical
        )
        critical_resource_name = ResourceName("criticalResourceName")
        critical_capability_availability = (
            self._resource_available_for_capability_in_period(
                critical_resource_name, Capability.skill("JAVA"), self.JAN_1_6
            )
        )

        planning_facade.plan_critical_stage_with_resource(
            project_id, critical_stage, critical_resource_name, self.JAN_4_8
        )

        self._verify_resources_not_available(
            project_id, critical_capability_availability, self.JAN_4_8
        )

        planning_facade.plan_critical_stage_with_resource(
            project_id, critical_stage, critical_resource_name, self.JAN_1_6
        )

        self._assert_resources_available(project_id, critical_capability_availability)

        schedule = planning_facade.load(project_id).schedule
        schedule_assert = ScheduleAssert(schedule)
        schedule_assert.assert_has_stage("Stage 1").assert_with_slot(self.JAN_1_2)
        schedule_assert.assert_has_stage("Stage 2").assert_with_slot(self.JAN_1_6)
        schedule_assert.assert_has_stage("Stage 3").assert_with_slot(self.JAN_1_4)

    def _assert_resources_available(
        self, project_id: ProjectId, resource: ResourceId
    ) -> None:
        pass

    def _verify_resources_not_available(
        self,
        project_id: ProjectId,
        resource: ResourceId,
        requested_but_not_available: TimeSlot,
    ) -> None:
        pass

    def _resource_available_for_capability_in_period(
        self, resource_name: ResourceName, capability: Capability, slot: TimeSlot
    ) -> ResourceId:
        return ResourceId.new_one()
