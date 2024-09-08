from lagom import Container

from smartschedule.shared.event_bus import EventBus
from smartschedule.shared.events_publisher import EventsPublisher


def build() -> Container:
    container = Container()
    container[EventsPublisher] = lambda c: EventBus(c)  # type: ignore[type-abstract]
    return container
