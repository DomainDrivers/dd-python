from datetime import datetime

from smartschedule.allocation.cashflow.cashflow import Cashflow
from smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from smartschedule.allocation.cashflow.income import Income
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.events_publisher import EventsPublisher


class CashFlowFacade:
    def __init__(
        self,
        cash_flow_repository: CashflowRepository,
        events_publisher: EventsPublisher,
    ) -> None:
        self._cash_flow_repository = cash_flow_repository
        self._events_publisher = events_publisher

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

        event = EarningsRecalculated(project_id, cashflow.earnings, datetime.now())
        self._events_publisher.publish(event)

    def find(self, project_id: ProjectAllocationsId) -> Earnings:
        cashflow = self._cash_flow_repository.get(project_id)
        return cashflow.earnings

    def find_all(self) -> dict[ProjectAllocationsId, Earnings]:
        cashflows = self._cash_flow_repository.get_all()
        return {cashflow.project_id: cashflow.earnings for cashflow in cashflows}
