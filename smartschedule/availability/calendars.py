from __future__ import annotations

from dataclasses import dataclass

from smartschedule.availability.calendar import Calendar
from smartschedule.availability.resource_id import ResourceId


@dataclass(frozen=True)
class Calendars:
    calendars: dict[ResourceId, Calendar]

    @staticmethod
    def of(*calendars: Calendar) -> Calendars:
        return Calendars({calendar.resource_id: calendar for calendar in calendars})

    def get(self, resource_id: ResourceId) -> Calendar:
        try:
            return self.calendars[resource_id]
        except KeyError:
            return Calendar.empty(resource_id)
