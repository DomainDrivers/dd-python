import abc

from smartschedule.shared.event import Event


class EventsPublisher(abc.ABC):
    @abc.abstractmethod
    def publish(self, event: Event) -> None:
        # remember about transactions scope
        pass
