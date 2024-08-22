from smartschedule.availability.resource_availability import ResourceAvailability
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestResourceAvailabilityLoading:
    ONE_MONTH = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)

    def test_saves_and_loads_by_id(
        self, repository: ResourceAvailabilityRepository
    ) -> None:
        resource_availablity_id = ResourceAvailabilityId.new_one()
        resource_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(
            resource_availablity_id, resource_id, self.ONE_MONTH
        )

        repository.save_new(resource_availability)

        loaded = repository.load_by_id(resource_availability.id)
        assert loaded == resource_availability
        assert loaded.segment == self.ONE_MONTH
        assert loaded.resource_id == resource_availability.resource_id
        assert loaded.blocked_by() == resource_availability.blocked_by()
