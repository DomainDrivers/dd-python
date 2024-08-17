from __future__ import annotations

from datetime import datetime
from typing import Self

from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.timeslot.time_slot import TimeSlot


class StageAssert:
    def __init__(self, actual: TimeSlot) -> None:
        self._actual = actual

    def assert_starts_at(self, start: datetime) -> None:
        __tracebackhide__ = True

        assert (
            self._actual.from_ == start
        ), f"Expected to start at {start}, but got {self._actual.from_}"

    def assert_with_slot(self, expected: TimeSlot) -> Self:
        __tracebackhide__ = True

        assert (
            self._actual == expected
        ), f"Expected to be {expected}, but got {self._actual}"
        return self

    def assert_ends_at(self, end: datetime) -> None:
        __tracebackhide__ = True

        assert (
            self._actual.to == end
        ), f"Expected to end at {end}, but got {self._actual.to}"

    def with_schedule(self, schedule: Schedule) -> StageScheduleAssert:
        return StageScheduleAssert(self._actual, schedule)


class StageScheduleAssert(StageAssert):
    def __init__(self, actual: TimeSlot, schedule: Schedule) -> None:
        super().__init__(actual)
        self._schedule = schedule

    def assert_is_before(self, stage_name: str) -> None:
        __tracebackhide__ = True

        schedule_from = self._schedule.dates[stage_name].from_

        assert (
            self._actual.to <= schedule_from
        ), f"Expected to be before {schedule_from}, but is not ({self._actual})"

    def assert_starts_together_with(self, stage_name: str) -> None:
        __tracebackhide__ = True

        schedule_from = self._schedule.dates[stage_name].from_

        assert (
            self._actual.from_ == schedule_from
        ), f"Expected to start together with {schedule_from}, but is not ({self._actual.from_})"

    def assert_is_after(self, stage_name: str) -> None:
        __tracebackhide__ = True

        schedule_to = self._schedule.dates[stage_name].to

        assert (
            self._actual.from_ >= schedule_to
        ), f"Expected to be after {schedule_to}, but is not ({self._actual})"
