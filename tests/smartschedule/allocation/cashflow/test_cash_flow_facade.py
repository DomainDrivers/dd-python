import pytest
from lagom import Container

from smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.income import Income
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId


@pytest.fixture()
def cash_flow_facade(container: Container) -> CashFlowFacade:
    return container.resolve(CashFlowFacade)


class TestCashFlowFacade:
    def test_saves_cashflow(self, cash_flow_facade: CashFlowFacade) -> None:
        project_id = ProjectAllocationsId.new_one()

        cash_flow_facade.add_income_and_cost(project_id, Income(100), Cost(50))

        earnings = cash_flow_facade.find(project_id)
        assert earnings == Earnings(50)
