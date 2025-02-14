from __future__ import annotations

from dataclasses import dataclass

from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class Calendar:
    resource_id: ResourceId
    calendar: dict[Owner, list[TimeSlot]]

    @staticmethod
    def with_available_slots(
        resource_id: ResourceId, *available_slots: TimeSlot
    ) -> Calendar:
        return Calendar(resource_id, {Owner.none(): list(available_slots)})

    @staticmethod
    def empty(resource_id: ResourceId) -> Calendar:
        return Calendar(resource_id, {})

    def available_slots(self) -> list[TimeSlot]:
        return self.calendar.get(Owner.none(), [])

    def taken_by(self, requster: Owner) -> list[TimeSlot]:
        return self.calendar.get(requster, [])
