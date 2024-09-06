import pytest
from lagom import Container

from smartschedule.resource.employee.employee_facade import EmployeeFacade


@pytest.fixture()
def employee_facade(container: Container) -> EmployeeFacade:
    return container.resolve(EmployeeFacade)
