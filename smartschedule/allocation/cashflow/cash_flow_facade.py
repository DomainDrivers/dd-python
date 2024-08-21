from smartschedule.allocation.cashflow.cashflow import Cashflow
from smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.income import Income
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId


class CashFlowFacade:
    def __init__(self, cash_flow_repository: CashflowRepository) -> None:
        self._cash_flow_repository = cash_flow_repository

    def add_income_and_cost(
        self, project_id: ProjectAllocationsId, income: Income, cost: Cost
    ) -> None:
        try:
            cashflow = self._cash_flow_repository.get(project_id)
            cashflow.income = income
            cashflow.cost = cost
        except self._cash_flow_repository.NotFound:
            cashflow = Cashflow(project_id=project_id, income=income, cost=cost)
            self._cash_flow_repository.add(cashflow)

    def find(self, project_id: ProjectAllocationsId) -> Earnings:
        cashflow = self._cash_flow_repository.get(project_id)
        return cashflow.earnings
