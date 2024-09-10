from __future__ import annotations

from datetime import timedelta
from typing import Final


class SegmentInMinutes:
    DEFAULT_SEGMENT_DURATION: Final = timedelta(minutes=60)
    DEFAULT_SEGMENT_DURATION_IN_MINUTES: Final = int(
        DEFAULT_SEGMENT_DURATION.total_seconds() / 60
    )

    _value: timedelta

    def __init__(self, minutes: int, slot_duration_in_minutes: int) -> None:
        if minutes <= 0:
            raise ValueError("SegmentInMinutesDuraton must be greater than 0")
        if minutes < slot_duration_in_minutes:
            raise ValueError(
                f"SegmentInMinutesDuraton must be at least {slot_duration_in_minutes} minutes"
            )
        if minutes % slot_duration_in_minutes != 0:
            raise ValueError(
                f"SegmentInMinutesDuraton must be a multiple of {slot_duration_in_minutes} minutes"
            )

        self._value = timedelta(minutes=minutes)

    @staticmethod
    def of(minutes: int) -> SegmentInMinutes:
        return SegmentInMinutes(
            minutes, SegmentInMinutes.DEFAULT_SEGMENT_DURATION_IN_MINUTES
        )

    @property
    def value(self) -> timedelta:
        return self._value

    @classmethod
    def default_segment(cls) -> SegmentInMinutes:
        return SegmentInMinutes(
            cls.DEFAULT_SEGMENT_DURATION_IN_MINUTES,
            cls.DEFAULT_SEGMENT_DURATION_IN_MINUTES,
        )
