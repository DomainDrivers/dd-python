import pytest
from lagom import Container

from smartschedule.resource.device.device_facade import DeviceFacade


@pytest.fixture()
def device_facade(container: Container) -> DeviceFacade:
    return container.resolve(DeviceFacade)
