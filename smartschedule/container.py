from lagom import Container

from smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from smartschedule.allocation.cashflow.sqlalchemy_cashflow_repository import (
    SqlAlchemyCashflowRepository,
)
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.allocation.sqlalchemy_project_allocations_repository import (
    SqlAlchemyProjectAllocationsRepository,
)
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.planning.sqlalchemy_project_repository import (
    SqlAlchemyProjectRepository,
)
from smartschedule.shared.event_bus import EventBus, SyncExecutor
from smartschedule.shared.events_publisher import EventsPublisher


def build() -> Container:
    container = Container()
    executor = SyncExecutor()
    container[EventsPublisher] = lambda c: EventBus(c, executor)  # type: ignore[type-abstract]
    container[EventBus] = lambda c: EventBus(c, executor)
    container[CashflowRepository] = SqlAlchemyCashflowRepository  # type: ignore[type-abstract]
    container[ProjectRepository] = SqlAlchemyProjectRepository  # type: ignore[type-abstract]
    container[ProjectAllocationsRepository] = SqlAlchemyProjectAllocationsRepository  # type: ignore[type-abstract]
    return container
