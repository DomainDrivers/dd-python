import pytest
from lagom import Container

from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)


@pytest.fixture()
def repository(container: Container) -> ResourceAvailabilityRepository:
    return container.resolve(ResourceAvailabilityRepository)
