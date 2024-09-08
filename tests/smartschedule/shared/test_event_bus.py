from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock

import pytest
from lagom import Container

from smartschedule.shared.event_bus import EventBus
from tests.timeout import timeout


@dataclass(frozen=True)
class DummyEvent:
    occurred_at: datetime


@pytest.fixture()
def event_bus(container: Container) -> EventBus:
    return container.resolve(EventBus)


class TestEventBus:
    def test_calls_listener(self, event_bus: EventBus) -> None:
        spy = Mock()

        @EventBus.has_event_handlers
        class DummyListener:
            @EventBus.async_event_handler
            def handle(self, event: DummyEvent) -> None:
                spy(event)

        event = DummyEvent(occurred_at=datetime.now())
        event_bus.publish(event)

        def assertions() -> None:
            assert spy.called
            spy.assert_called_once_with(event)

        timeout(milliseconds=1000, callable=assertions)
