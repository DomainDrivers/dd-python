import abc
from typing import Sequence

from smartschedule.allocation.cashflow.cashflow import Cashflow
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId


class CashflowRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, project_id: ProjectAllocationsId) -> Cashflow:
        pass

    @abc.abstractmethod
    def get_all(
        self, ids: list[ProjectAllocationsId] | None = None
    ) -> Sequence[Cashflow]:
        pass

    @abc.abstractmethod
    def add(self, cashflow: Cashflow) -> None:
        pass
