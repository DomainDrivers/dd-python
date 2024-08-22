from datetime import datetime

import pytest

from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.availability.segment.slot_to_normalized_slot import (
    slot_to_normalized_slot,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestSlotToNormalizedSlod:
    def test_has_no_effect_when_slot_already_normalized(self) -> None:
        start = datetime(2023, 9, 9)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)
        one_hour = SegmentInMinutes(60)

        normalized = slot_to_normalized_slot(time_slot, one_hour)

        assert time_slot == normalized

    def test_normalization_to_1_hour(self) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 0, 59)
        time_slot = TimeSlot(start, end)
        one_hour = SegmentInMinutes(60)

        normalized = slot_to_normalized_slot(time_slot, one_hour)

        assert normalized == TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1))

    def test_normalized_short_slot_overlapping_two_segments(self) -> None:
        start = datetime(2023, 9, 9, 0, 29)
        end = datetime(2023, 9, 9, 0, 31)
        time_slot = TimeSlot(start, end)
        one_hour = SegmentInMinutes(60)

        normalized = slot_to_normalized_slot(time_slot, one_hour)

        assert normalized == TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1))

    @pytest.mark.parametrize(
        "start, end",
        [
            (datetime(2023, 9, 9, 0, 15), datetime(2023, 9, 9, 0, 30)),
            (datetime(2023, 9, 9, 0, 30), datetime(2023, 9, 9, 0, 45)),
        ],
    )
    def test_no_normalization_when_slot_starts_at_segment_start(
        self, start: datetime, end: datetime
    ) -> None:
        fifteen_minutes = SegmentInMinutes(15)

        normalized = slot_to_normalized_slot(TimeSlot(start, end), fifteen_minutes)

        assert normalized == TimeSlot(start, end)
