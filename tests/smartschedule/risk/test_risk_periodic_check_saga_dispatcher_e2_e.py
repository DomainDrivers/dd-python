from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Final, Iterator
from unittest.mock import Mock
from uuid import uuid4

import pytest
import time_machine
from lagom import Container

from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from smartschedule.allocation.cashflow.income import Income
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
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
from tests.timeout import timeout


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
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduled(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )

        event = CapabilitiesAllocated(
            uuid4(), project_id, Demands.none(), datetime.now()
        )
        self.risk_saga_dispatcher.handle_capabilities_allocated(event)

        risk_push_notification_mock.notify_demands_satisfied.assert_called_once_with(
            project_id
        )

    def test_informs_about_potential_risk_when_resource_taken_over(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduled(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )
        self.risk_saga_dispatcher.handle_capabilities_allocated(
            CapabilitiesAllocated(uuid4(), project_id, Demands.none(), datetime.now())
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

    def test_weekly_check_does_nothing_when_not_too_close_to_deadline_and_demands_not_satisfied(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduled(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduled(project_id, self.PROJECT_DATES, datetime.now())
        )

        with self._days_before_deadline(100):
            self.risk_saga_dispatcher.handle_weekly_check()

        assert len(risk_push_notification_mock.mock_calls) == 0

    def test_weekly_check_does_nothing_when_close_to_deadline_and_demands_satisfied(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR-UNIQUE")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduled(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )
        self.risk_saga_dispatcher.handle_earnings_recalculated(
            EarningsRecalculated(project_id, Earnings(10), datetime.now())
        )
        self.risk_saga_dispatcher.handle_capabilities_allocated(
            CapabilitiesAllocated(uuid4(), project_id, Demands.none(), datetime.now())
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduled(project_id, self.PROJECT_DATES, datetime.now())
        )

        risk_push_notification_mock.reset_mock()
        with self._days_before_deadline(100):
            self.risk_saga_dispatcher.handle_weekly_check()

        assert len(risk_push_notification_mock.mock_calls) == 0

    def test_find_replacements_when_deadline_is_close(
        self, risk_push_notification_mock: Mock
    ) -> None:
        project_id = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.risk_saga_dispatcher.handle_project_allocations_demands_scheduled(
            ProjectAllocationsDemandsScheduled(
                project_id, Demands.of(java_one_day_demand), datetime.now()
            )
        )
        self.risk_saga_dispatcher.handle_earnings_recalculated(
            EarningsRecalculated(project_id, Earnings(10), datetime.now())
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduled(project_id, self.PROJECT_DATES, datetime.now())
        )
        employee_id = self._employee_with_skills({java}, self.ONE_DAY_LONG)

        risk_push_notification_mock.reset_mock()
        with self._days_before_deadline(20):
            self.risk_saga_dispatcher.handle_weekly_check()

        assert (
            len(risk_push_notification_mock.notify_about_availability.mock_calls) == 1
        )
        called_with_project_id, available = (
            risk_push_notification_mock.notify_about_availability.mock_calls[0].args
        )
        assert called_with_project_id == project_id
        suggested_capabilities = {ac.id for ac in available[java_one_day_demand].all}
        assert employee_id in suggested_capabilities

    def test_suggest_resources_from_different_projects(
        self, risk_push_notification_mock: Mock
    ) -> None:
        high_value_project = ProjectAllocationsId.new_one()
        low_value_project = ProjectAllocationsId.new_one()
        java = Capability.skill("JAVA-MID-JUNIOR-SUPER-UNIQUE")
        java_one_day_demand = Demand(java, self.ONE_DAY_LONG)
        self.allocation_facade.schedule_project_allocations_demands(
            high_value_project, Demands.of(java_one_day_demand)
        )
        self.cash_flow_facade.add_income_and_cost(
            high_value_project, Income(10000), Cost(10)
        )
        self.allocation_facade.schedule_project_allocations_demands(
            low_value_project, Demands.of(java_one_day_demand)
        )
        self.cash_flow_facade.add_income_and_cost(
            low_value_project, Income(100), Cost(10)
        )
        employee_id = self._employee_with_skills({java}, self.ONE_DAY_LONG)
        self.allocation_facade.allocate_to_project(
            low_value_project, employee_id, self.ONE_DAY_LONG
        )
        self.risk_saga_dispatcher.handle_project_allocations_scheduled(
            ProjectAllocationScheduled(
                high_value_project, self.PROJECT_DATES, datetime.now()
            )
        )

        risk_push_notification_mock.reset_mock()
        self.allocation_facade.edit_project_dates(
            high_value_project, self.PROJECT_DATES
        )
        self.allocation_facade.edit_project_dates(low_value_project, self.PROJECT_DATES)
        with self._days_before_deadline(1):
            self.risk_saga_dispatcher.handle_weekly_check()

        def assertions() -> None:
            risk_push_notification_mock.notify_profitable_relocation_found.assert_called_once_with(
                high_value_project, employee_id
            )

        timeout(milliseconds=1000, callable=assertions)

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
