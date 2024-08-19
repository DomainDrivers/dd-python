from datetime import timedelta

from smartschedule.planning.parallelization.duration_calculator import (
    calculate_duration,
)
from smartschedule.planning.parallelization.stage import Stage


class TestDurationCalculator:
    def test_longest_stage_is_taken_into_account(self) -> None:
        stage_1 = Stage("Stage 1", duration=timedelta())
        stage_2 = Stage("Stage 2", duration=timedelta(days=3))
        stage_3 = Stage("Stage 3", duration=timedelta(days=2))
        stage_4 = Stage("Stage 4", duration=timedelta(days=5))

        duration = calculate_duration([stage_1, stage_2, stage_3, stage_4])

        assert duration == timedelta(days=5)

    def test_sum_is_taken_into_account_when_nothing_is_parallel(self) -> None:
        stage_1 = Stage("Stage 1", duration=timedelta(hours=10))
        stage_2 = Stage("Stage 2", duration=timedelta(hours=24))
        stage_3 = Stage("Stage 3", duration=timedelta(days=2))
        stage_4 = Stage("Stage 4", duration=timedelta(days=1))
        stage_4.depends_on(stage_3)
        stage_3.depends_on(stage_2)
        stage_2.depends_on(stage_1)

        duration = calculate_duration([stage_1, stage_2, stage_3, stage_4])

        assert duration == timedelta(hours=106)
