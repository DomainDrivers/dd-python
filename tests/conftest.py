import time
from typing import Callable, Iterator

import pytest
from lagom import Container
from redis import Redis
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer  # type: ignore
from testcontainers.redis import RedisContainer  # type: ignore

from smartschedule import container as container_module
from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.resource.employee.employee_facade import EmployeeFacade
from smartschedule.shared.sqlalchemy_extensions import registry


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgres:15") as container:
        yield container


@pytest.fixture(scope="session")
def redis_container() -> Iterator[RedisContainer]:
    with RedisContainer("redis:6") as container:
        yield container


@pytest.fixture(scope="session")
def engine_for_tests(postgres_container: PostgresContainer) -> Engine:
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=True)

    # There seems to be some race condition. Fine, let's wait.
    start = time.monotonic()
    while time.monotonic() - start < 30:
        try:
            engine.connect()
            break
        except Exception:
            time.sleep(0.1)

    registry.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def session_factory(engine_for_tests: Engine) -> Callable[[], Session]:
    return sessionmaker(bind=engine_for_tests)


@pytest.fixture()
def session(session_factory: Callable[[], Session]) -> Iterator[Session]:
    a_session = session_factory()
    yield a_session
    a_session.close()


@pytest.fixture()
def clean_redis(redis_container: RedisContainer) -> Iterator[None]:
    client = redis_container.get_client()
    client.flushall()
    yield


@pytest.fixture()
def container(
    session: Session, redis_container: RedisContainer, clean_redis: None
) -> Container:
    container = container_module.build()
    container[Session] = session
    container[Redis] = redis_container.get_client()
    return container


@pytest.fixture()
def availability_facade(container: Container) -> AvailabilityFacade:
    return container.resolve(AvailabilityFacade)


@pytest.fixture()
def capability_finder(container: Container) -> CapabilityFinder:
    return container.resolve(CapabilityFinder)


@pytest.fixture()
def employee_facade(container: Container) -> EmployeeFacade:
    return container.resolve(EmployeeFacade)


@pytest.fixture()
def planning_facade(container: Container) -> PlanningFacade:
    return container.resolve(PlanningFacade)


@pytest.fixture()
def allocation_facade(container: Container) -> AllocationFacade:
    return container.resolve(AllocationFacade)


@pytest.fixture()
def cash_flow_facade(container: Container) -> CashFlowFacade:
    return container.resolve(CashFlowFacade)
