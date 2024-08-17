from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.schedule.calendars import Calendars
from smartschedule.planning.schedule.schedule_based_on_chosen_resources_availability_calculator import (
    ScheduleBasedOnChosenResourcesAvailabilityCalculator,
)
from smartschedule.planning.schedule.schedule_based_on_reference_stage_calculator import (
    ScheduleBasedOnReferenceStageCalculator,
)
from smartschedule.planning.schedule.schedule_based_on_start_day_calculator import (
    ScheduleBasedOnStartDayCalculator,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class Schedule:
    dates: dict[str, TimeSlot]

    @staticmethod
    def none() -> Schedule:
        return Schedule({})

    @staticmethod
    def based_on_start_day(
        start_date: date, parallelized_stages: ParallelStagesList
    ) -> Schedule:
        schedule_dict = ScheduleBasedOnStartDayCalculator().calculate(
            start_date, parallelized_stages, printing_comparator
        )
        return Schedule(schedule_dict)

    @staticmethod
    def based_on_reference_stage_time_slots(
        reference_stage: Stage,
        stage_proposed_time_slot: TimeSlot,
        parallelized_stages: ParallelStagesList,
    ) -> Schedule:
        schedule_dict = ScheduleBasedOnReferenceStageCalculator().calculate(
            reference_stage,
            stage_proposed_time_slot,
            parallelized_stages,
            printing_comparator,
        )
        return Schedule(schedule_dict)

    @staticmethod
    def based_on_chosen_resource_availability(
        chosen_resources_calendars: Calendars, stages: list[Stage]
    ) -> Schedule:
        schedule_dict = (
            ScheduleBasedOnChosenResourcesAvailabilityCalculator().calculate(
                chosen_resources_calendars,
                stages,
            )
        )
        return Schedule(schedule_dict)


def printing_comparator(parallel_stages: ParallelStages) -> int:
    print(parallel_stages)
    return 0
