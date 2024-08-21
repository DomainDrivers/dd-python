import pytest
from lagom import Container

from smartschedule.allocation.allocation_facade import AllocationFacade


@pytest.fixture()
def allocation_facade(container: Container) -> AllocationFacade:
    return container.resolve(AllocationFacade)
