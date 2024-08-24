import pytest
from lagom import Container

from smartschedule.resource.employee.employee_facade import EmployeeFacade
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability


@pytest.fixture()
def employee_facade(container: Container) -> EmployeeFacade:
    return container.resolve(EmployeeFacade)


class TestCreatingEmployee:
    def test_creates_and_loads_employee(self, employee_facade: EmployeeFacade) -> None:
        employee_id = employee_facade.add_employee(
            "John",
            "Doe",
            Seniority.SENIOR,
            Capability.skills("JAVA", "PYTHON"),
            Capability.permissions("ADMIN", "COURT"),
        )

        loaded = employee_facade.find_employee(employee_id)

        assert loaded.skills == Capability.skills("JAVA", "PYTHON")
        assert loaded.permissions == Capability.permissions("ADMIN", "COURT")
        assert loaded.name == "John"
        assert loaded.last_name == "Doe"
        assert loaded.seniority == Seniority.SENIOR

    def test_finds_all_capabilities(self, employee_facade: EmployeeFacade) -> None:
        employee_facade.add_employee(
            "staszek",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA12", "PYTHON21"),
            Capability.permissions("ADMIN1", "COURT1"),
        )
        employee_facade.add_employee(
            "leon",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA12", "PYTHON21"),
            Capability.permissions("ADMIN2", "COURT2"),
        )
        employee_facade.add_employee(
            "sławek",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA12", "PYTHON21"),
            Capability.permissions("ADMIN3", "COURT3"),
        )

        loaded = employee_facade.find_all_capabilities()

        assert set(loaded) == {
            Capability("JAVA12", "SKILL"),
            Capability("PYTHON21", "SKILL"),
            Capability("ADMIN1", "PERMISSION"),
            Capability("COURT1", "PERMISSION"),
            Capability("ADMIN2", "PERMISSION"),
            Capability("COURT2", "PERMISSION"),
            Capability("ADMIN3", "PERMISSION"),
            Capability("COURT3", "PERMISSION"),
        }
