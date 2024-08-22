from __future__ import annotations

from datetime import timedelta
from typing import Final


class SegmentInMinutes:
    DEFAULT_SEGMENT_DURATION: Final = timedelta(minutes=15)

    _value: timedelta

    def __init__(self, minutes: int) -> None:
        if minutes <= 0:
            raise ValueError("SegmentInMinutesDuraton must be greater than 0")
        default_duration_in_minutes = (
            int(self.DEFAULT_SEGMENT_DURATION.total_seconds()) / 60
        )
        if minutes % default_duration_in_minutes != 0:
            raise ValueError(
                f"SegmentInMinutesDuration must be a multiple of {default_duration_in_minutes}"
            )

        self._value = timedelta(minutes=minutes)

    @property
    def value(self) -> timedelta:
        return self._value

    @classmethod
    def default_segment(cls) -> SegmentInMinutes:
        return SegmentInMinutes(int(cls.DEFAULT_SEGMENT_DURATION.total_seconds() / 60))
