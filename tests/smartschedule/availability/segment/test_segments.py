from datetime import datetime

import pytest

from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.availability.segment.segments import (
    normalize_to_segment_boundaries,
    split,
)
from smartschedule.availability.segment.slot_to_segments import slot_to_segments
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestSegments:
    @pytest.mark.parametrize("value", [20, 18, 7])
    def test_segment_cannot_be_created_with_number_not_being_multiply_of_15(
        self, value: int
    ) -> None:
        with pytest.raises(ValueError):
            SegmentInMinutes(value)

    @pytest.mark.parametrize("value", [15, 30, 45])
    def test_segment_can_be_created_with_number_being_multiply_of_15(
        self, value: int
    ) -> None:
        try:
            SegmentInMinutes(value)
        except ValueError:
            pytest.fail(
                "SegmentInMinutes should be created with number being multiply of 15"
            )

    def test_splitting_to_segments_when_there_is_no_leftover(self) -> None:
        start = datetime(2023, 9, 9)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)

        segments = split(time_slot, SegmentInMinutes(15))

        assert segments == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 0, 15)),
            TimeSlot(datetime(2023, 9, 9, 0, 15), datetime(2023, 9, 9, 0, 30)),
            TimeSlot(datetime(2023, 9, 9, 0, 30), datetime(2023, 9, 9, 0, 45)),
            TimeSlot(datetime(2023, 9, 9, 0, 45), datetime(2023, 9, 9, 1)),
        ]

    def test_splitting_normalizes_if_chosen_segment_larger_than_passed_slot(
        self,
    ) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)

        segments = split(time_slot, SegmentInMinutes(90))

        assert segments == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1, 30)),
        ]

    def test_normalizing_a_time_slot(self) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 1)
        time_slot = TimeSlot(start, end)

        segment = normalize_to_segment_boundaries(time_slot, SegmentInMinutes(90))

        assert segment == TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1, 30))

    def test_slots_are_normalized_before_splitting(self) -> None:
        start = datetime(2023, 9, 9, 0, 10)
        end = datetime(2023, 9, 9, 0, 59)
        time_slot = TimeSlot(start, end)

        segments = split(time_slot, SegmentInMinutes(60))

        assert segments == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 1)),
        ]

    def test_splitting_into_segments_without_normalization(self) -> None:
        start = datetime(2023, 9, 9)
        end = datetime(2023, 9, 9, 0, 59)
        time_slot = TimeSlot(start, end)

        segments = slot_to_segments(time_slot, SegmentInMinutes(30))

        assert segments == [
            TimeSlot(datetime(2023, 9, 9), datetime(2023, 9, 9, 0, 30)),
            TimeSlot(datetime(2023, 9, 9, 0, 30), datetime(2023, 9, 9, 0, 59)),
        ]
