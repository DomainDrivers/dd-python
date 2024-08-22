from concurrent.futures import ThreadPoolExecutor

from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability import ResourceAvailability
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestResourceAvailabilityOptimisticLocking:
    ONE_MONTH = TimeSlot.create_monthly_time_slot_at_utc(2021, 1)

    def test_update_bumps_version(
        self, repository: ResourceAvailabilityRepository
    ) -> None:
        resource_availability_id = ResourceAvailabilityId.new_one()
        resource_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(
            resource_availability_id, resource_id, self.ONE_MONTH
        )
        repository.save_new(resource_availability)

        loaded = repository.load_by_id(resource_availability.id)
        loaded.block(Owner.new_one())
        repository.save_checking_version(loaded)

        loaded_again = repository.load_by_id(resource_availability.id)
        assert loaded_again.version == 1

    def test_cant_update_concurrently(
        self, repository: ResourceAvailabilityRepository
    ) -> None:
        resource_availability_id = ResourceAvailabilityId.new_one()
        resource_id = ResourceAvailabilityId.new_one()
        resource_availability = ResourceAvailability(
            resource_availability_id, resource_id, self.ONE_MONTH
        )
        repository.save_new(resource_availability)

        results: list[bool] = []

        def try_to_block() -> None:
            loaded = repository.load_by_id(resource_availability.id)
            loaded.block(Owner.new_one())
            result = repository.save_checking_version(loaded)
            results.append(result)

        pool = ThreadPoolExecutor(max_workers=5)
        with pool:
            for _ in range(10):
                pool.submit(try_to_block)

        assert results.count(True) > 0
        assert results.count(False) > 0
        loaded = repository.load_by_id(resource_availability.id)
        assert loaded.version < 10
