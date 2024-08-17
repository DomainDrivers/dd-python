from smartschedule.planning.schedule.schedule import Schedule
from tests.smartschedule.planning.schedule.assertions.stage_assert import (
    StageScheduleAssert,
)


class ScheduleAssert:
    def __init__(self, schedule: Schedule) -> None:
        self._schedule = schedule

    def assert_has_stages(self, number: int) -> None:
        __tracebackhide__ = True

        actual = len(self._schedule.dates)
        assert actual == number, f"Expected to have {number} stages, but got {actual}"

    def assert_has_stage(self, stage_name: str) -> StageScheduleAssert:
        __tracebackhide__ = True

        all_stages_names = list(self._schedule.dates.keys())
        assert (
            stage_name in all_stages_names
        ), f"Expected to have stage {stage_name}, but not found in {all_stages_names}"
        return StageScheduleAssert(self._schedule.dates[stage_name], self._schedule)

    def assert_is_empty(self) -> None:
        __tracebackhide__ = True

        assert not self._schedule.dates, "Expected to be empty, but it's not"
