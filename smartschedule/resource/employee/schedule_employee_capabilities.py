from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.capability_scheduler import (
    CapabilityScheduler,
)
from smartschedule.resource.employee.employee_allocation_policy import (
    EmployeeAllocationPolicy,
)
from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.employee_repository import EmployeeRepository
from smartschedule.resource.employee.employee_summary import EmployeeSummary
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ScheduleEmployeeCapabilities:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        capability_scheduler: CapabilityScheduler,
    ) -> None:
        self._employee_repository = employee_repository
        self._capability_scheduler = capability_scheduler

    def setup_employee_capabilities(
        self, employee_id: EmployeeId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        summary = self._employee_repository.find_summary(employee_id)
        policy = self._find_allocation_policy(summary)
        capabilities = policy.simultaneous_capabilities_of(summary)
        return self._capability_scheduler.schedule_resource_capabilities_for_period(
            employee_id.to_allocatable_resource_id(), capabilities, time_slot
        )

    def _find_allocation_policy(
        self, summary: EmployeeSummary
    ) -> EmployeeAllocationPolicy:
        if summary.seniority == Seniority.LEAD:
            return EmployeeAllocationPolicy.simultaneous(
                EmployeeAllocationPolicy.one_of_skills(),
                EmployeeAllocationPolicy.permissions_in_multiple_projects(3),
            )
        return EmployeeAllocationPolicy.default_policy()
