import pytest

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestTakingRandomResource:
    @pytest.fixture(autouse=True)
    def setup(self, availability_facade: AvailabilityFacade) -> None:
        self._availability = availability_facade

    def test_can_take_random_resource_from_pool(self) -> None:
        resource_id = ResourceId.new_one()
        resource_id2 = ResourceId.new_one()
        resource_id3 = ResourceId.new_one()
        resources_pool = {resource_id, resource_id2, resource_id3}
        owner_1 = Owner.new_one()
        owner_2 = Owner.new_one()
        owner_3 = Owner.new_one()
        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        self._availability.create_resource_slots(resource_id, one_day)
        self._availability.create_resource_slots(resource_id2, one_day)
        self._availability.create_resource_slots(resource_id3, one_day)

        taken_1 = self._availability.block_random_available(
            resources_pool, one_day, owner_1
        )
        assert taken_1 in resources_pool
        assert self._resource_is_taken_by_owner(taken_1, owner_1, one_day)

        taken_2 = self._availability.block_random_available(
            resources_pool, one_day, owner_2
        )
        assert taken_2 in resources_pool
        assert self._resource_is_taken_by_owner(taken_2, owner_2, one_day)

        taken_3 = self._availability.block_random_available(
            resources_pool, one_day, owner_3
        )
        assert taken_3 in resources_pool
        assert self._resource_is_taken_by_owner(taken_3, owner_3, one_day)

        taken_4 = self._availability.block_random_available(
            resources_pool, one_day, owner_3
        )
        assert taken_4 is None

    def test_nothing_is_taken_when_no_resource_in_pool(self) -> None:
        resources = {ResourceId.new_one(), ResourceId.new_one(), ResourceId.new_one()}
        jan_1 = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)

        taken_1 = self._availability.block_random_available(
            resources, jan_1, Owner.new_one()
        )

        assert taken_1 is None

    def _resource_is_taken_by_owner(
        self, resource_id: ResourceId, owner: Owner, one_day: TimeSlot
    ) -> bool:
        resource_availability = self._availability.find(resource_id, one_day)
        return all(
            availability.blocked_by() == owner
            for availability in resource_availability.resource_availabilities
        )
