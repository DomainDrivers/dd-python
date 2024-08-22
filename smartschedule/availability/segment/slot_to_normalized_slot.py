from datetime import datetime

from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.shared.timeslot.time_slot import TimeSlot


def slot_to_normalized_slot(
    time_slot: TimeSlot, segment_in_minutes: SegmentInMinutes
) -> TimeSlot:
    segment_start = _normalize_start(time_slot.from_, segment_in_minutes)
    segment_end = _normalize_end(time_slot.to, segment_in_minutes)
    normalized = TimeSlot(segment_start, segment_end)
    minimal_segment = TimeSlot(segment_start, segment_start + segment_in_minutes.value)
    if normalized.within(minimal_segment):
        return minimal_segment
    return normalized


def _normalize_start(
    initial_start: datetime, segment_in_minutes: SegmentInMinutes
) -> datetime:
    closest_segment_start = initial_start.replace(minute=0, second=0, microsecond=0)
    if closest_segment_start + segment_in_minutes.value > initial_start:
        return closest_segment_start
    while closest_segment_start < initial_start:
        closest_segment_start += segment_in_minutes.value
    return closest_segment_start


def _normalize_end(
    initial_end: datetime, segment_in_minutes: SegmentInMinutes
) -> datetime:
    closest_segment_end = initial_end.replace(minute=0, second=0, microsecond=0)
    while initial_end > closest_segment_end:
        closest_segment_end += segment_in_minutes.value
    return closest_segment_end
