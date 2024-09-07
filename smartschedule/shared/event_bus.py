from lagom import Container

from smartschedule.shared.event import Event
from smartschedule.shared.events_publisher import EventsPublisher


class EventBus(EventsPublisher):
    def __init__(self, container: Container) -> None:
        self._container = container

    def publish_after_commit(self, event: Event) -> None:
        # could grab a session from the container
        # and append new 'after commit' event handler
        pass
