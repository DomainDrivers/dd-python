from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)
from smartschedule.availability.resource_grouped_availability import (
    ResourceGroupedAvailability,
)
from smartschedule.availability.segment import segments
from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.shared.timeslot.time_slot import TimeSlot


class AvailabilityFacade:
    def __init__(self, repository: ResourceAvailabilityRepository) -> None:
        self._repository = repository

    def create_resource_slots(
        self,
        resource_id: ResourceAvailabilityId,
        time_slot: TimeSlot,
        parent_id: ResourceAvailabilityId | None = None,
    ) -> None:
        grouped_availability = ResourceGroupedAvailability.of(
            resource_id, time_slot, parent_id
        )
        self._repository.save_new(grouped_availability)

    def block(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        to_block = self._find_grouped(resource_id, time_slot)
        return self._block(to_block, requester)

    def _block(self, to_block: ResourceGroupedAvailability, requester: Owner) -> bool:
        result = to_block.block(requester)
        if result:
            return self._repository.save_checking_version(to_block)
        else:
            return False

    def release(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        to_release = self._find_grouped(resource_id, time_slot)
        result = to_release.release(requester)
        if result:
            return self._repository.save_checking_version(to_release)
        else:
            return False

    def disable(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        to_disable = self._find_grouped(resource_id, time_slot)
        result = to_disable.disable(requester)
        if result:
            return self._repository.save_checking_version(to_disable)
        else:
            return False

    def _find_grouped(
        self, resource_id: ResourceAvailabilityId, within: TimeSlot
    ) -> ResourceGroupedAvailability:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        availabilities = self._repository.load_all_within_slot(resource_id, normalized)
        return ResourceGroupedAvailability(availabilities)

    def find(
        self, resource_id: ResourceAvailabilityId, within: TimeSlot
    ) -> ResourceGroupedAvailability:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        availabilities = self._repository.load_all_within_slot(resource_id, normalized)
        return ResourceGroupedAvailability(availabilities)

    def find_by_parent_id(
        self, parent_id: ResourceAvailabilityId, within: TimeSlot
    ) -> ResourceGroupedAvailability:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        availabilities = self._repository.load_all_by_parent_id_within_slot(
            parent_id, normalized
        )
        return ResourceGroupedAvailability(availabilities)
