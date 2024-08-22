import math
from datetime import datetime

from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.shared.timeslot.time_slot import TimeSlot


def slot_to_segments(time_slot: TimeSlot, duration: SegmentInMinutes) -> list[TimeSlot]:
    minimal_segment = TimeSlot(time_slot.from_, time_slot.from_ + duration.value)
    if time_slot.within(minimal_segment):
        return [minimal_segment]
    number_of_segments = _calculate_number_of_segments(time_slot, duration)

    current_start = time_slot.from_
    result = []
    for _ in range(number_of_segments):
        current_end = _calculate_end(duration, current_start, time_slot.to)
        slot = TimeSlot(current_start, current_end)
        result.append(slot)
        current_start = current_start + duration.value
    return result


def _calculate_number_of_segments(
    time_slot: TimeSlot, duration: SegmentInMinutes
) -> int:
    return math.ceil(
        time_slot.duration.total_seconds() / duration.value.total_seconds()
    )


def _calculate_end(
    duration: SegmentInMinutes, current_start: datetime, initial_end: datetime
) -> datetime:
    return min(current_start + duration.value, initial_end)
