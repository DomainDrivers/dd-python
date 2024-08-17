from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from smartschedule.planning.parallelization.resource_name import ResourceName
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class Calendars:
    calendars: dict[ResourceName, Calendar]

    @staticmethod
    def of(*calendars: Calendar) -> Calendars:
        return Calendars({calendar.resource_id: calendar for calendar in calendars})

    def get(self, resource_id: ResourceName) -> Calendar:
        try:
            return self.calendars[resource_id]
        except KeyError:
            return Calendar.empty(resource_id)


@dataclass(frozen=True)
class Calendar:
    resource_id: ResourceName
    calendar: dict[Owner, list[TimeSlot]]

    @staticmethod
    def with_available_slots(
        resource_id: ResourceName, *available_slots: TimeSlot
    ) -> Calendar:
        return Calendar(resource_id, {Owner.none(): list(available_slots)})

    @staticmethod
    def empty(resource_id: ResourceName) -> Calendar:
        return Calendar(resource_id, {})

    def available_slots(self) -> list[TimeSlot]:
        return self.calendar.get(Owner.none(), [])


@dataclass(frozen=True)
class Owner:
    owner: UUID | None

    @staticmethod
    def none() -> Owner:
        return Owner(None)
