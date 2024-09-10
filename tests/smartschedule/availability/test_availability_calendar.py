from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestAvailabilityCalendar:
    def test_loads_calendar_for_entire_month(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        duration_of_seven_slots = 7 * SegmentInMinutes.DEFAULT_SEGMENT_DURATION
        seven_slots = TimeSlot.create_daily_time_slot_at_utc_duration(
            2021, 1, 1, duration_of_seven_slots
        )
        minimum_slot = TimeSlot(
            seven_slots.from_,
            seven_slots.from_ + SegmentInMinutes.DEFAULT_SEGMENT_DURATION,
        )
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, seven_slots)

        availability_facade.block(resource_id, minimum_slot, owner)

        calendar = availability_facade.load_calendar(resource_id, seven_slots)
        assert calendar.taken_by(owner) == [minimum_slot]
        assert (
            calendar.available_slots()
            == seven_slots.leftover_after_removing_common_with(minimum_slot)
        )

    def test_loads_calendar_for_multiple_resources(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        resource_id2 = ResourceId.new_one()
        duration_of_seven_slots = 7 * SegmentInMinutes.DEFAULT_SEGMENT_DURATION
        seven_slots = TimeSlot.create_daily_time_slot_at_utc_duration(
            2021, 1, 1, duration_of_seven_slots
        )
        minimum_slot = TimeSlot(
            seven_slots.from_,
            seven_slots.from_ + SegmentInMinutes.DEFAULT_SEGMENT_DURATION,
        )
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, seven_slots)
        availability_facade.create_resource_slots(resource_id2, seven_slots)

        availability_facade.block(resource_id, minimum_slot, owner)
        availability_facade.block(resource_id2, minimum_slot, owner)

        calendars = availability_facade.load_calendars(
            {resource_id, resource_id2}, seven_slots
        )
        calendar_1 = calendars.get(resource_id)
        assert calendar_1.taken_by(owner) == [minimum_slot]
        assert (
            calendar_1.available_slots()
            == seven_slots.leftover_after_removing_common_with(minimum_slot)
        )
        calendar_2 = calendars.get(resource_id2)
        assert calendar_2.taken_by(owner) == [minimum_slot]
        assert (
            calendar_2.available_slots()
            == seven_slots.leftover_after_removing_common_with(minimum_slot)
        )
