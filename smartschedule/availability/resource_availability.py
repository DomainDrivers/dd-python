from typing import Final

from smartschedule.availability.blockade import Blockade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ResourceAvailability:
    def __init__(
        self,
        id: ResourceAvailabilityId,
        resource_id: ResourceId,
        segment: TimeSlot,
        parent_id: ResourceId | None = None,
        blockade: Blockade | None = None,
        version: int = 0,
    ) -> None:
        if parent_id is None:
            parent_id = ResourceId.new_one()

        if blockade is None:
            blockade = Blockade.none()

        self.id: Final = id
        self.resource_id: Final = resource_id
        self.parent_id: Final = parent_id
        self.segment: Final = segment
        self.blockade = blockade
        self.version = version

    def block(self, requester: Owner) -> bool:
        if self._is_available_for(requester):
            self.blockade = self.blockade.owned_by(requester)
            return True
        else:
            return False

    def release(self, requester: Owner) -> bool:
        if self._is_available_for(requester):
            self.blockade = self.blockade.none()
            return True
        else:
            return False

    def disable(self, requester: Owner) -> bool:
        self.blockade = Blockade.disabled_by(requester)
        return True

    def enable(self, requester: Owner) -> bool:
        if self.blockade.can_be_taken_by(requester):
            self.blockade = self.blockade.none()
            return True
        else:
            return False

    def is_disabled(self) -> bool:
        return self.blockade.disabled

    def is_disabled_by(self, requester: Owner) -> bool:
        return self.blockade.is_disabled_by(requester)

    def _is_available_for(self, requester: Owner) -> bool:
        return self.blockade.can_be_taken_by(requester) and not self.is_disabled()

    def blocked_by(self) -> Owner:
        return self.blockade.taken_by

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ResourceAvailability) and value.id == self.id
