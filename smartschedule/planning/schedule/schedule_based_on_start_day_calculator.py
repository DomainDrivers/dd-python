from datetime import date, datetime
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
        current_start = datetime.combine(start_date, datetime.min.time())
        all_sorted = parallelized_stages.all_sorted(sort_key_getter=sort_key_getter)
        for stages in all_sorted:
            parallelized_stages_end = current_start
            for stage in stages.stages:
                stage_end = current_start + stage.duration
                schedule_dict[stage.name] = TimeSlot(current_start, stage_end)
                if stage_end > parallelized_stages_end:
                    parallelized_stages_end = stage_end
            current_start = parallelized_stages_end
        return schedule_dict
