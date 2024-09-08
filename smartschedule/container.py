from lagom import Container

from smartschedule.shared.event_bus import EventBus, SyncExecutor
from smartschedule.shared.events_publisher import EventsPublisher


def build() -> Container:
    container = Container()
    executor = SyncExecutor()
    container[EventsPublisher] = lambda c: EventBus(c, executor)  # type: ignore[type-abstract]
    container[EventBus] = lambda c: EventBus(c, executor)
    return container
