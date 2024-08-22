from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.availability.segment.slot_to_normalized_slot import (
    slot_to_normalized_slot,
)
from smartschedule.availability.segment.slot_to_segments import slot_to_segments
from smartschedule.shared.timeslot.time_slot import TimeSlot


def split(time_slot: TimeSlot, unit: SegmentInMinutes) -> list[TimeSlot]:
    normalized_slot = normalize_to_segment_boundaries(time_slot, unit)
    return slot_to_segments(normalized_slot, unit)


def normalize_to_segment_boundaries(
    time_slot: TimeSlot, unit: SegmentInMinutes
) -> TimeSlot:
    return slot_to_normalized_slot(time_slot, unit)
