import pytest
from lagom import Container

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.resource_availability_repository import (
    ResourceAvailabilityRepository,
)


@pytest.fixture()
def repository(container: Container) -> ResourceAvailabilityRepository:
    return container.resolve(ResourceAvailabilityRepository)


@pytest.fixture()
def availability_facade(container: Container) -> AvailabilityFacade:
    return container.resolve(AvailabilityFacade)
