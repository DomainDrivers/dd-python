from __future__ import annotations

from typing import Final

from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability import ResourceAvailability
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_id import ResourceId
from smartschedule.availability.segment import segments
from smartschedule.availability.segment.segment_in_minutes import SegmentInMinutes
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ResourceGroupedAvailability:
    def __init__(self, resource_availabilities: list[ResourceAvailability]) -> None:
        self.resource_availabilities: Final = resource_availabilities

    @staticmethod
    def of(
        resource_id: ResourceId,
        timeslot: TimeSlot,
        parent_id: ResourceId | None = None,
    ) -> ResourceGroupedAvailability:
        resource_availabilities = [
            ResourceAvailability(
                id=ResourceAvailabilityId.new_one(),
                resource_id=resource_id,
                segment=segment,
                parent_id=parent_id,
            )
            for segment in segments.split(timeslot, SegmentInMinutes.default_segment())
        ]
        return ResourceGroupedAvailability(resource_availabilities)

    def block(self, requester: Owner) -> bool:
        return all(
            resource_availability.block(requester)
            for resource_availability in self.resource_availabilities
        )

    def disable(self, requester: Owner) -> bool:
        return all(
            resource_availability.disable(requester)
            for resource_availability in self.resource_availabilities
        )

    def release(self, requester: Owner) -> bool:
        return all(
            resource_availability.release(requester)
            for resource_availability in self.resource_availabilities
        )

    @property
    def resource_id(self) -> ResourceId | None:
        if len(self.resource_availabilities) > 0:
            return self.resource_availabilities[0].resource_id
        else:
            return None

    def __len__(self) -> int:
        return len(self.resource_availabilities)

    def blocked_entirely_by(self, owner: Owner) -> bool:
        return all(
            resource_availability.blocked_by() == owner
            for resource_availability in self.resource_availabilities
        )

    def is_disabled_entirely_by(self, owner: Owner) -> bool:
        return all(
            resource_availability.is_disabled_by(owner)
            for resource_availability in self.resource_availabilities
        )

    def find_blocked_by(self, owner: Owner) -> list[ResourceAvailability]:
        return [
            resource_availability
            for resource_availability in self.resource_availabilities
            if resource_availability.blocked_by() == owner
        ]

    def is_entirely_available(self) -> bool:
        return all(
            resource_availability.blocked_by().by_none()
            for resource_availability in self.resource_availabilities
        )

    def has_no_slots(self) -> bool:
        return len(self.resource_availabilities) == 0
