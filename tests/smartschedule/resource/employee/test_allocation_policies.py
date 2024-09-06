import itertools

from smartschedule.resource.employee.employee_allocation_policy import (
    EmployeeAllocationPolicy,
)
from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.employee_summary import EmployeeSummary
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import CapabilitySelector


class TestAllocationPolicies:
    def test_default_policy_returns_just_one_skill_at_once(self) -> None:
        summary = EmployeeSummary(
            EmployeeId.new_one(),
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA"),
            Capability.permissions("ADMIN"),
        )

        capabilities = (
            EmployeeAllocationPolicy.default_policy().simultaneous_capabilities_of(
                summary
            )
        )

        assert len(capabilities) == 1
        assert capabilities[0].capabilities == {
            Capability.skill("JAVA"),
            Capability.permission("ADMIN"),
        }

    def test_permissions_can_be_shared_between_projects(self) -> None:
        policy = EmployeeAllocationPolicy.permissions_in_multiple_projects(3)
        employee = EmployeeSummary(
            EmployeeId.new_one(),
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA"),
            Capability.permissions("ADMIN"),
        )

        capabilities = policy.simultaneous_capabilities_of(employee)

        assert len(capabilities) == 3
        all_capabilities = list(
            itertools.chain(*[c.capabilities for c in capabilities])
        )
        assert all_capabilities == [Capability.permission("ADMIN")] * 3

    def test_can_create_composite_policy(self) -> None:
        policy = EmployeeAllocationPolicy.simultaneous(
            EmployeeAllocationPolicy.permissions_in_multiple_projects(3),
            EmployeeAllocationPolicy.one_of_skills(),
        )
        summary = EmployeeSummary(
            EmployeeId.new_one(),
            "resourceName",
            "lastName",
            Seniority.LEAD,
            Capability.skills("JAVA", "PYTHON"),
            Capability.permissions("ADMIN"),
        )

        capabilities = policy.simultaneous_capabilities_of(summary)

        assert len(capabilities) == 4
        assert (
            CapabilitySelector.can_perform_one_of(Capability.skills("JAVA", "PYTHON"))
            in capabilities
        )
        assert (
            capabilities.count(
                CapabilitySelector.can_just_perform(Capability.permission("ADMIN"))
            )
            == 3
        )
