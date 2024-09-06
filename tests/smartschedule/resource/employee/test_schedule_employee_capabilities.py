from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.resource.employee.employee_facade import EmployeeFacade
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestScheduleEmployeeCapabilities:
    def test_can_setup_capabilities_according_to_policy(
        self, employee_facade: EmployeeFacade, capability_finder: CapabilityFinder
    ) -> None:
        employee_id = employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA, PYTHON"),
            Capability.permissions("ADMIN"),
        )

        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocations = employee_facade.schedule_capabilities(employee_id, one_day)

        loaded = capability_finder.find_by_id(allocations)
        assert len(loaded.all) == len(allocations)
