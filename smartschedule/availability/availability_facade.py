from smartschedule.availability.calendar import Calendar
from smartschedule.availability.calendars import Calendars
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability_read_model import (
    ResourceAvailabilityReadModel,
)
from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)
from smartschedule.availability.resource_grouped_availability import (
    ResourceGroupedAvailability,
)
from smartschedule.availability.resource_id import ResourceId
from smartschedule.availability.segment import segments
from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.shared.timeslot.time_slot import TimeSlot


class AvailabilityFacade:
    def __init__(
        self,
        repository: ResourceAvailabilityRepository,
        read_model: ResourceAvailabilityReadModel,
    ) -> None:
        self._repository = repository
        self._read_model = read_model

    def create_resource_slots(
        self,
        resource_id: ResourceId,
        time_slot: TimeSlot,
        parent_id: ResourceId | None = None,
    ) -> None:
        grouped_availability = ResourceGroupedAvailability.of(
            resource_id, time_slot, parent_id
        )
        self._repository.save_new(grouped_availability)

    def block(
        self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        to_block = self._find_grouped(resource_id, time_slot)
        return self._block(to_block, requester)

    def _block(self, to_block: ResourceGroupedAvailability, requester: Owner) -> bool:
        if to_block.has_no_slots():
            return False

        result = to_block.block(requester)
        if result:
            return self._repository.save_checking_version(to_block)
        else:
            return False

    def release(
        self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        to_release = self._find_grouped(resource_id, time_slot)
        if to_release.has_no_slots():
            return False
        result = to_release.release(requester)
        if result:
            return self._repository.save_checking_version(to_release)
        else:
            return False

    def disable(
        self, resource_id: ResourceId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        to_disable = self._find_grouped(resource_id, time_slot)
        if to_disable.has_no_slots():
            return False

        result = to_disable.disable(requester)
        if result:
            return self._repository.save_checking_version(to_disable)
        else:
            return False

    def _find_grouped(
        self, resource_id: ResourceId, within: TimeSlot
    ) -> ResourceGroupedAvailability:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        availabilities = self._repository.load_all_within_slot(resource_id, normalized)
        return ResourceGroupedAvailability(availabilities)

    def find(
        self, resource_id: ResourceId, within: TimeSlot
    ) -> ResourceGroupedAvailability:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        availabilities = self._repository.load_all_within_slot(resource_id, normalized)
        return ResourceGroupedAvailability(availabilities)

    def find_by_parent_id(
        self, parent_id: ResourceId, within: TimeSlot
    ) -> ResourceGroupedAvailability:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        availabilities = self._repository.load_all_by_parent_id_within_slot(
            parent_id, normalized
        )
        return ResourceGroupedAvailability(availabilities)

    def load_calendar(self, resource_id: ResourceId, within: TimeSlot) -> Calendar:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        return self._read_model.load(resource_id, normalized)

    def load_calendars(
        self, resource_ids: set[ResourceId], within: TimeSlot
    ) -> Calendars:
        normalized = segments.normalize_to_segment_boundaries(
            within, SegmentInMinutes.default_segment()
        )
        return self._read_model.load_all(resource_ids, normalized)
