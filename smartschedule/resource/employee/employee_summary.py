from dataclasses import dataclass

from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability


@dataclass(frozen=True)
class EmployeeSummary:
    id: EmployeeId
    name: str
    last_name: str
    seniority: Seniority
    skills: set[Capability]
    permissions: set[Capability]
