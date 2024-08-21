from datetime import timedelta

import pytest
from lagom import Container

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def availability_facade(container: Container) -> AvailabilityFacade:
    return container.resolve(AvailabilityFacade)


class TestAvailabilityFacade:
    def test_creates_availability_slots(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        availability_facade.create_resource_slots(resource_id, one_day)

        # TODO: check that availability(ies) was/were created

    def test_blocks_availabilities(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is True
        # TODO: check that can't be taken

    def test_disable_availabilities(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        result = availability_facade.disable(resource_id, one_day, owner)

        assert result is True
        # TODO: check that are disabled

    def test_cannot_block_when_even_just_small_segment_of_requested_slot_is_blocked(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        availability_facade.block(resource_id, fifteen_minutes, owner)

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is False
        # TODO: check that nothing was changed

    def test_release_availability(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, fifteen_minutes)
        availability_facade.block(resource_id, fifteen_minutes, owner)

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is True
        # TODO: check can be taken again

    def test_cant_release_when_just_part_of_slot_is_owned_by_another_requester(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceAvailabilityId.new_one()
        jan_1 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        jan_2 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 2)
        jan_1_2 = TimeSlot(jan_1.from_, jan_2.to)
        jan_1_owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, jan_1_2)
        availability_facade.block(resource_id, jan_1, jan_1_owner)
        jan_2_owner = Owner.new_one()
        availability_facade.block(resource_id, jan_2, jan_2_owner)

        result = availability_facade.release(resource_id, jan_1_2, jan_1_owner)

        assert result is False
        # TODO: check still owned by jan1
