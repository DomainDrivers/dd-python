import inspect
import logging
from collections import defaultdict
from concurrent.futures import Executor
from concurrent.futures._base import Future
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Final, ParamSpec, Type, TypeAlias, TypeVar

from lagom import Container

from smartschedule.shared.events_publisher import EventsPublisher
from smartschedule.shared.published_event import PublishedEvent

logger = logging.getLogger(__name__)

ClassWithEventHandlers: TypeAlias = Type[object]
EventHandler: TypeAlias = Callable[[Any, PublishedEvent], None]


P = ParamSpec("P")
T = TypeVar("T")


class SyncExecutor(Executor):
    def submit(
        self, fn: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs
    ) -> Future[T]:
        result = fn(*args, **kwargs)
        future: Future[T] = Future()
        future.set_result(result)
        return future


@dataclass(frozen=True)
class ClassBasedHandler:
    class_: ClassWithEventHandlers
    method: EventHandler


EVENT_HANDLER_EVENT_TYPE_ATTR: Final = "__event_bus_handling_event__"

F = TypeVar("F", bound=Callable[..., Any])


class EventBus(EventsPublisher):
    __handlers: ClassVar[dict[Type[PublishedEvent], list[ClassBasedHandler]]] = (
        defaultdict(list)
    )

    def __init__(self, container: Container, executor: Executor) -> None:
        self._container = container
        self._executor = executor

    def publish(self, event: PublishedEvent) -> None:
        handlers = self.__handlers[type(event)]
        for handler in handlers:

            def task() -> None:
                try:
                    instance = self._container.resolve(handler.class_)
                    handler.method(instance, event)
                except Exception:
                    logger.exception(
                        "Error while handling event %r in handler %r", event, handler
                    )

            self._executor.submit(task)

    @classmethod
    def has_event_handlers(cls, class_: Type[T]) -> Type[T]:
        # iter over methods
        # if method has __event_bus_handling_event__ attribute
        # add to __handlers
        methods = inspect.getmembers(class_, predicate=inspect.isfunction)
        event_handlers = [
            method
            for _, method in methods
            if hasattr(method, EVENT_HANDLER_EVENT_TYPE_ATTR)
        ]
        for handler in event_handlers:
            event_type = getattr(handler, EVENT_HANDLER_EVENT_TYPE_ATTR)
            cls.__handlers[event_type].append(ClassBasedHandler(class_, handler))

        return class_

    @classmethod
    def async_event_handler(cls, func: F) -> F:
        arg_spec = inspect.getfullargspec(func)
        annotations = {k: v for k, v in arg_spec.annotations.items() if k != "return"}
        if len(annotations) != 1:
            raise ValueError("Event handler must accept exactly one argument")

        event_type = next(iter(annotations.values()))
        setattr(func, EVENT_HANDLER_EVENT_TYPE_ATTR, event_type)
        return func
