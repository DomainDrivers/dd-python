from smartschedule.availability.calendars import Calendars


class AvailabilityFacade:
    def availabilities_of_resources(self) -> Calendars:
        return Calendars.of()  # TODO
