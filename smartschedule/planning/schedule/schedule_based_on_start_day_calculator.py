from datetime import date
from typing import Callable

from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.shared.typing_extensions import Comparable


class ScheduleBasedOnStartDayCalculator:
    def calculate(
        self,
        start_date: date,
        parallelized_stages: ParallelStagesList,
        sort_key_getter: Callable[[ParallelStages], Comparable],
    ) -> dict[str, TimeSlot]:
        schedule_dict: dict[str, TimeSlot] = {}
        current_start = start_date  # noqa
        all_sorted = parallelized_stages.all_sorted(sort_key_getter=sort_key_getter)  # noqa
        # TODO
        return schedule_dict
