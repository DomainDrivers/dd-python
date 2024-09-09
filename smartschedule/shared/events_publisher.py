import abc

from smartschedule.shared.published_event import PublishedEvent


class EventsPublisher(abc.ABC):
    @abc.abstractmethod
    def publish(self, event: PublishedEvent) -> None:
        pass
