from smartschedule.resource.employee.employee import Employee
from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.employee_repository import EmployeeRepository
from smartschedule.resource.employee.employee_summary import EmployeeSummary
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability


class EmployeeFacade:
    def __init__(self, repository: EmployeeRepository) -> None:
        self._repository = repository

    def find_employee(self, employee_id: EmployeeId) -> EmployeeSummary:
        return self._repository.find_summary(employee_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self._repository.find_all_capabilities()

    def add_employee(
        self,
        name: str,
        last_name: str,
        seniority: Seniority,
        skills: set[Capability],
        permissions: set[Capability],
    ) -> EmployeeId:
        employee_id = EmployeeId.new_one()
        capabilities = skills | permissions
        employee = Employee(employee_id, name, last_name, seniority, capabilities)
        self._repository.add(employee)
        return employee.id

    # TODO: add vacation, call availability
    # TODO: add sick leave, call availability
    # change skills
