import pytest

from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability import ResourceAvailability
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def resource_availability() -> ResourceAvailability:
    return ResourceAvailability(
        id=TestResourceAvailability.RESOURCE_AVAILABILITY_ID,
        resource_id=ResourceId.new_one(),
        segment=TimeSlot.create_daily_time_slot_at_utc(2000, 1, 1),
    )


class TestResourceAvailability:
    RESOURCE_AVAILABILITY_ID = ResourceAvailabilityId.new_one()
    OWNER_1 = Owner.new_one()
    OWNER_2 = Owner.new_one()

    def test_can_block_when_available(
        self, resource_availability: ResourceAvailability
    ) -> None:
        result = resource_availability.block(self.OWNER_1)

        assert result is True

    def test_cant_be_blocked_when_blocked_by_someone_else(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.block(self.OWNER_1)

        result = resource_availability.block(self.OWNER_2)

        assert result is False

    def test_can_be_released_by_owner(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.block(self.OWNER_1)

        result = resource_availability.release(self.OWNER_1)

        assert result is True

    def test_cant_be_released_by_someone_else(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.block(self.OWNER_1)

        result = resource_availability.release(self.OWNER_2)

        assert result is False

    def test_can_be_blocked_by_someone_else_after_releasing(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.block(self.OWNER_1)
        resource_availability.release(self.OWNER_1)

        result = resource_availability.block(self.OWNER_2)

        assert result is True

    def test_can_be_disabled_when_available(
        self, resource_availability: ResourceAvailability
    ) -> None:
        result = resource_availability.disable(self.OWNER_1)

        assert result is True
        assert resource_availability.is_disabled()
        assert resource_availability.is_disabled_by(self.OWNER_1)

    def test_can_disable_when_blocked(
        self, resource_availability: ResourceAvailability
    ) -> None:
        result_blocking = resource_availability.block(self.OWNER_1)

        result_disabling = resource_availability.disable(self.OWNER_2)

        assert result_blocking is True
        assert result_disabling is True
        assert resource_availability.is_disabled()
        assert resource_availability.is_disabled_by(self.OWNER_2)

    def test_cant_be_blocked_when_disabled(
        self, resource_availability: ResourceAvailability
    ) -> None:
        result_disabling = resource_availability.disable(self.OWNER_1)

        result_blocking = resource_availability.block(self.OWNER_2)
        result_blocking_by_owner = resource_availability.block(self.OWNER_1)

        assert result_disabling is True
        assert result_blocking is False
        assert result_blocking_by_owner is False
        assert resource_availability.is_disabled()
        assert resource_availability.is_disabled_by(self.OWNER_1)

    def test_can_be_enabled_by_initial_requester(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.disable(self.OWNER_1)

        result = resource_availability.enable(self.OWNER_1)

        assert result is True
        assert not resource_availability.is_disabled()
        assert not resource_availability.is_disabled_by(self.OWNER_1)

    def test_cant_be_enabled_by_another_requester(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.disable(self.OWNER_1)

        result = resource_availability.enable(self.OWNER_2)

        assert result is False
        assert resource_availability.is_disabled()
        assert resource_availability.is_disabled_by(self.OWNER_1)

    def test_can_be_blocked_again_after_enabling(
        self, resource_availability: ResourceAvailability
    ) -> None:
        resource_availability.disable(self.OWNER_1)
        resource_availability.enable(self.OWNER_1)

        result = resource_availability.block(self.OWNER_2)

        assert result is True
