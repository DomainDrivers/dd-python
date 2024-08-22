from datetime import timedelta

import pytest
from lagom import Container

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def availability_facade(container: Container) -> AvailabilityFacade:
    return container.resolve(AvailabilityFacade)


class TestAvailabilityFacade:
    def test_creates_availability_slots(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        availability_facade.create_resource_slots(resource_id, one_day)

        grouped = availability_facade.find(resource_id, one_day)
        assert len(grouped) == 96

    def test_creates_new_availability_slots_with_parent_id(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        resource_id2 = ResourceId.new_one()
        parent_id = ResourceId.new_one()
        different_parent_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        availability_facade.create_resource_slots(resource_id, one_day, parent_id)
        availability_facade.create_resource_slots(
            resource_id2, one_day, different_parent_id
        )

        assert len(availability_facade.find_by_parent_id(parent_id, one_day)) == 96
        assert (
            len(availability_facade.find_by_parent_id(different_parent_id, one_day))
            == 96
        )

    def test_blocks_availabilities(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        result = availability_facade.block(resource_id, one_day, owner)

        assert result is True
        availabilities = availability_facade.find(resource_id, one_day)
        assert len(availabilities) == 96
        assert availabilities.blocked_entirely_by(owner)

    def test_disable_availabilities(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)

        result = availability_facade.disable(resource_id, one_day, owner)

        assert result is True
        availabilities = availability_facade.find(resource_id, one_day)
        assert len(availabilities) == 96
        assert availabilities.is_disabled_entirely_by(owner)

    def test_cannot_block_when_even_just_small_segment_of_requested_slot_is_blocked(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        availability_facade.block(resource_id, fifteen_minutes, owner)

        result = availability_facade.block(resource_id, one_day, Owner.new_one())

        assert result is False
        availabilities = availability_facade.find(resource_id, one_day)
        availabilities.blocked_entirely_by(owner)

    def test_release_availability(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, fifteen_minutes)
        availability_facade.block(resource_id, fifteen_minutes, owner)

        result = availability_facade.release(resource_id, one_day, owner)

        assert result is True
        availabilities = availability_facade.find(resource_id, one_day)
        assert availabilities.is_entirely_available()

    def test_cant_release_when_just_part_of_slot_is_owned_by_another_requester(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
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
        availabilities = availability_facade.find(resource_id, jan_1)
        assert availabilities.blocked_entirely_by(jan_1_owner)

    def test_one_segment_can_taken_by_someone_else_after_releasing(
        self, availability_facade: AvailabilityFacade
    ) -> None:
        resource_id = ResourceId.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        fifteen_minutes = TimeSlot(one_day.from_, one_day.from_ + timedelta(minutes=15))
        owner = Owner.new_one()
        availability_facade.create_resource_slots(resource_id, one_day)
        availability_facade.block(resource_id, one_day, owner)
        availability_facade.release(resource_id, fifteen_minutes, owner)

        new_requester = Owner.new_one()
        result = availability_facade.block(resource_id, fifteen_minutes, new_requester)

        assert result is True
        availabilities = availability_facade.find(resource_id, one_day)
        assert len(availabilities) == 96
        assert len(availabilities.find_blocked_by(new_requester)) == 1
        assert len(availabilities.find_blocked_by(owner)) == 95
