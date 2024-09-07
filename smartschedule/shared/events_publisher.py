import abc

from smartschedule.shared.event import Event


class EventsPublisher(abc.ABC):
    @abc.abstractmethod
    def publish_after_commit(self, event: Event) -> None:
        pass
