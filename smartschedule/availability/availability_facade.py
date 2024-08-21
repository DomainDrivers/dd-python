from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class AvailabilityFacade:
    def create_resource_slots(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot
    ) -> None:
        pass

    def block(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        return True

    def release(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        return True

    def disable(
        self, resource_id: ResourceAvailabilityId, time_slot: TimeSlot, requester: Owner
    ) -> bool:
        return True
