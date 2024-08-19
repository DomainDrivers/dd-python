from datetime import timedelta
from typing import Iterable

from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.parallelization.stage_parallelization import (
    StageParallelization,
)


def calculate_duration(stages: Iterable[Stage]) -> timedelta:
    parallelized_stages = StageParallelization().of(set(stages))
    return sum(
        (parallel_stages.duration for parallel_stages in parallelized_stages.all),
        timedelta(),
    )
