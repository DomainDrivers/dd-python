import pytest
from sqlalchemy.exc import IntegrityError

from smartschedule.availability.resource_availability import ResourceAvailability
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestResourceAvailabilityUniqueness:
    ONE_MONTH = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)

    def test_cant_save_two_availabilities_with_the_same_resource_id_and_segment(
        self, repository: ResourceAvailabilityRepository
    ) -> None:
        resource_id = ResourceId.new_one()
        another_resource_id = ResourceId.new_one()
        resource_availability_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(
            resource_availability_id, resource_id, self.ONE_MONTH
        )
        repository.save_new(resource_availability)

        another_resource_availability = ResourceAvailability(
            resource_availability_id, another_resource_id, self.ONE_MONTH
        )

        with pytest.raises(IntegrityError):
            repository.save_new(another_resource_availability)
