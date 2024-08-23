from datetime import timedelta

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestAvailabilityCalendar:
    def test_loads_calendar_for_entire_month(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(
            one_day.from_ + timedelta(minutes=15), one_day.from_ + timedelta(minutes=30)
        )
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        availability_facade.block(resource_id, fifteen_minutes, owner)

        calendar = availability_facade.load_calendar(resource_id, one_day)
        assert calendar.taken_by(owner) == [fifteen_minutes]
        assert (
            calendar.available_slots()
            == one_day.leftover_after_removing_common_with(fifteen_minutes)
        )

    def test_loads_calendar_for_multiple_resources(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        resource_id2 = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(
            one_day.from_ + timedelta(minutes=15), one_day.from_ + timedelta(minutes=30)
        )
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)
        availability_facade.create_resource_slots(resource_id2, one_day)

        availability_facade.block(resource_id, fifteen_minutes, owner)
        availability_facade.block(resource_id2, fifteen_minutes, owner)

        calendars = availability_facade.load_calendars(
            {resource_id, resource_id2}, one_day
        )
        calendar_1 = calendars.get(resource_id)
        assert calendar_1.taken_by(owner) == [fifteen_minutes]
        assert (
            calendar_1.available_slots()
            == one_day.leftover_after_removing_common_with(fifteen_minutes)
        )
        calendar_2 = calendars.get(resource_id2)
        assert calendar_2.taken_by(owner) == [fifteen_minutes]
        assert (
            calendar_2.available_slots()
            == one_day.leftover_after_removing_common_with(fifteen_minutes)
        )
