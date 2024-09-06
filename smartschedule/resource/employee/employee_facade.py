from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.resource.employee.employee import Employee
from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.employee_repository import EmployeeRepository
from smartschedule.resource.employee.employee_summary import EmployeeSummary
from smartschedule.resource.employee.schedule_employee_capabilities import (
    ScheduleEmployeeCapabilities,
)
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class EmployeeFacade:
    def __init__(
        self,
        repository: EmployeeRepository,
        schedule_employee_capabilities: ScheduleEmployeeCapabilities,
    ) -> None:
        self._repository = repository
        self._schedule_employee_capabilities = schedule_employee_capabilities

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

    def schedule_capabilities(
        self, employee_id: EmployeeId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        return self._schedule_employee_capabilities.setup_employee_capabilities(
            employee_id, time_slot
        )

    # TODO: add vacation, call availability
    # TODO: add sick leave, call availability
    # change skills
