from smartschedule.resource.employee.employee import Employee
from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.employee_summary import EmployeeSummary
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class EmployeeRepository(SQLAlchemyRepository[Employee, EmployeeId]):
    def find_summary(self, employee_id: EmployeeId) -> EmployeeSummary:
        employee = self.get(employee_id)
        skills = {
            capability
            for capability in employee.capabilities
            if capability.is_of_type("SKILL")
        }
        permissions = {
            capability
            for capability in employee.capabilities
            if capability.is_of_type("PERMISSION")
        }
        return EmployeeSummary(
            id=employee.id,
            name=employee.name,
            last_name=employee.last_name,
            seniority=employee.seniority,
            skills=skills,
            permissions=permissions,
        )

    def find_all_capabilities(self) -> list[Capability]:
        employees = self.get_all()
        return [
            capability for employee in employees for capability in employee.capabilities
        ]
