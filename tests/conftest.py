import time
from typing import Callable, Iterator

import pytest
from lagom import Container
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer  # type: ignore

from smartschedule.shared.sqlalchemy_extensions import registry


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgres:15") as container:
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
def container(session: Session) -> Container:
    container = Container()
    container[Session] = session
    return container
