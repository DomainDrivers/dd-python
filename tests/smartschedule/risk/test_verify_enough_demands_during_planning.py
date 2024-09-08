from typing import Any
from unittest.mock import Mock

import pytest
from lagom import Container

from smartschedule.planning.demand import Demand
from smartschedule.planning.demands import Demands
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.resource.employee.employee_facade import EmployeeFacade
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.risk.risk_push_notification import RiskPushNotification
from smartschedule.shared.capability.capability import Capability
from tests.timeout import timeout, timeout_never


@pytest.fixture()
def risk_push_notification_mock() -> Any:
    return Mock(spec_set=RiskPushNotification)


class TestVerifyEnoughDemandsDuringPlanning:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        employee_facade: EmployeeFacade,
        planning_facade: PlanningFacade,
        risk_push_notification_mock: Any,
        container: Container,
    ) -> None:
        self.employee_facade = employee_facade
        self.planning_facade = planning_facade
        container[RiskPushNotification] = risk_push_notification_mock
        # Python Magic.
        # Class has to be imported to be interpreted, so listeners can be registered
        from smartschedule.risk.verify_enough_demands_during_planning import (
            VerifyEnoughDemandsDuringPlanning,  # noqa: F401
        )

    def test_does_nothing_when_enough_resources(
        self, risk_push_notification_mock: Any
    ) -> None:
        self.employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA5", "PYTHON"),
            Capability.permissions(),
        )
        self.employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("C#", "RUST"),
            Capability.permissions(),
        )
        project_id = self.planning_facade.add_new_project("java5")

        self.planning_facade.add_demands(
            project_id, Demands.of(Demand.for_(Capability.skill("JAVA5")))
        )

        def assertions() -> None:
            assert risk_push_notification_mock.called

        timeout_never(milliseconds=1000, callable=assertions)

    def test_notifies_when_not_enough_resources(
        self, risk_push_notification_mock: Any
    ) -> None:
        self.employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("JAVA"),
            Capability.permissions(),
        )
        self.employee_facade.add_employee(
            "resourceName",
            "lastName",
            Seniority.SENIOR,
            Capability.skills("C"),
            Capability.permissions(),
        )
        java_project_id = self.planning_facade.add_new_project("java")
        c_project_id = self.planning_facade.add_new_project("C")
        self.planning_facade.add_demands(
            java_project_id, Demands.of(Demand.for_(Capability.skill("JAVA")))
        )
        self.planning_facade.add_demands(
            c_project_id, Demands.of(Demand.for_(Capability.skill("C")))
        )
        rust_project_id = self.planning_facade.add_new_project("rust")
        self.planning_facade.add_demands(
            rust_project_id, Demands.of(Demand.for_(Capability.skill("RUST")))
        )

        def assertions() -> None:
            risk_push_notification_mock.notify_about_possible_risk_during_planning.assert_called_once_with(
                rust_project_id, Demands.of(Demand.for_(Capability.skill("RUST")))
            )

        timeout(milliseconds=1000, callable=assertions)
