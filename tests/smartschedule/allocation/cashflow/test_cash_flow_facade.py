from typing import Any

import pytest
from lagom import Container
from mockito import verify  # type: ignore
from mockito.matchers import arg_that  # type: ignore

from smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from smartschedule.allocation.cashflow.income import Income
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.event_bus import EventBus


@pytest.fixture()
def cash_flow_facade(container: Container) -> CashFlowFacade:
    return container.resolve(CashFlowFacade)


class TestCashFlowFacade:
    def test_saves_cashflow(self, cash_flow_facade: CashFlowFacade) -> None:
        project_id = ProjectAllocationsId.new_one()

        cash_flow_facade.add_income_and_cost(project_id, Income(100), Cost(50))

        earnings = cash_flow_facade.find(project_id)
        assert earnings == Earnings(50)

    def test_updating_cash_flow_emits_an_event(
        self, cash_flow_facade: CashFlowFacade, when: Any
    ) -> None:
        when(EventBus).publish(...)
        project_id = ProjectAllocationsId.new_one()
        income = Income(100)
        cost = Cost(50)

        cash_flow_facade.add_income_and_cost(project_id, income, cost)

        verify(EventBus).publish(
            arg_that(
                lambda event: self._is_earnings_recalculated_event(
                    event, project_id, Earnings(50)
                )
            )
        )

    def _is_earnings_recalculated_event(
        self, event: Any, project_id: ProjectAllocationsId, earnings: Earnings
    ) -> Any:
        return (
            isinstance(event, EarningsRecalculated)
            and event.project_id == project_id
            and event.earnings == earnings
        )
