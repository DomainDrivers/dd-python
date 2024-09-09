from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Final, Iterator
from unittest.mock import Mock, call

import pytest
import time_machine
from lagom import Container

from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_id import ResourceId
from smartschedule.availability.resource_taken_over import ResourceTakenOver
from smartschedule.resource.employee.employee_facade import EmployeeFacade
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.risk.risk_periodic_check_saga_dispatcher import (
    RiskPeriodicCheckSagaDispatcher,
)
from smartschedule.risk.risk_push_notification import RiskPushNotification
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def risk_push_notification_mock() -> Mock:
    return Mock(spec_set=RiskPushNotification)


@pytest.fixture(autouse=True)
def configure_risk_notification_mock(
    risk_push_notification_mock: Mock, container: Container
) -> None:
    container[RiskPushNotification] = risk_push_notification_mock


@pytest.fixture()
def risk_saga_dispatcher(container: Container) -> RiskPeriodicCheckSagaDispatcher:
    return container.resolve(RiskPeriodicCheckSagaDispatcher)


class TestRiskPeriodicCheckSagaDispatcherE2E:
    ONE_DAY_LONG: Final = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    PROJECT_DATES: Final = TimeSlot(
        datetime.now(),
        datetime.now() + timedelta(days=20),
    )

    @pytest.fixture(autouse=True)
    def setup(
        self,
        employee_facade: EmployeeFacade,
        allocation_facade: AllocationFacade,
        risk_saga_dispatcher: RiskPeriodicCheckSagaDispatcher,
        cash_flow_facade: CashFlowFacade,
    ) -> None:
        self.employee_facade = employee_facade
        self.allocation_facade = allocation_facade
        self.risk_saga_dispatcher = risk_saga_dispatcher
        self.cash_flow_facade = cash_flow_facade

    def test_informs_about_demand_satisfied(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_not_satisfied_demands(
            NotSatisfiedDemands.for_one_project(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )

        self.risk_saga_dispatcher.handle_not_satisfied_demands(
            NotSatisfiedDemands.all_satisfied(project_id, datetime.now())
        )

        risk_push_notification_mock.notify_demands_satisfied.assert_called_once_with(
            project_id
        )

    def test_informs_about_demand_satisfied_for_all_projects(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        project_id2 = ProjectAllocationsId.new_one()
        no_missing_demands = {project_id: Demands.none(), project_id2: Demands.none()}

        self.risk_saga_dispatcher.handle_not_satisfied_demands(
            NotSatisfiedDemands(no_missing_demands, datetime.now())
        )

        risk_push_notification_mock.notify_demands_satisfied.assert_has_calls(
            [call(project_id), call(project_id2)], any_order=True
        )

    def test_informs_about_potential_risk_when_resource_taken_over(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_not_satisfied_demands(
            NotSatisfiedDemands.for_one_project(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )
        self.risk_saga_dispatcher.handle_not_satisfied_demands(
            NotSatisfiedDemands.all_satisfied(project_id, datetime.now())
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduled(project_id, self.PROJECT_DATES, datetime.now())
        )

        risk_push_notification_mock.reset_mock()
        with self._days_before_deadline(100):
            event = ResourceTakenOver(
                ResourceId.new_one(),
                {Owner(project_id.id)},
                self.ONE_DAY_LONG,
                datetime.now(),
            )
            self.risk_saga_dispatcher.handle_resource_taken_over(event)

        risk_push_notification_mock.notify_about_possible_risk.assert_called_once_with(
            project_id
        )

    def test_does_nothing_when_resource_taken_from_unknown_project(
        self, risk_push_notification_mock: Mock
    ) -> None:
        unknown_project_id = ProjectAllocationsId.new_one()

        event = ResourceTakenOver(
            ResourceId.new_one(),
            {Owner(unknown_project_id.id)},
            self.ONE_DAY_LONG,
            datetime.now(),
        )
        self.risk_saga_dispatcher.handle_resource_taken_over(event)

        assert len(risk_push_notification_mock.mock_calls) == 0

    @contextmanager
    def _days_before_deadline(self, days: int) -> Iterator[None]:
        date_to_set = self.PROJECT_DATES.to - timedelta(days=days)
        with time_machine.travel(date_to_set, tick=False):
            yield

    def _employee_with_skills(
        self, skills: set[Capability], in_slot: TimeSlot
    ) -> AllocatableCapabilityId:
        staszek = self.employee_facade.add_employee(
            "Staszek", "Staszkowski", Seniority.MID, skills, Capability.permissions()
        )
        allocatable_capability_ids = self.employee_facade.schedule_capabilities(
            staszek, in_slot
        )
        return allocatable_capability_ids[0]
