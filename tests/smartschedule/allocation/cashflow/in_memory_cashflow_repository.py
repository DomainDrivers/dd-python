from copy import deepcopy
from typing import Sequence

from smartschedule.allocation.cashflow.cashflow import Cashflow
from smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.repository import NotFound


class InMemoryCashflowRepository(CashflowRepository):
    def __init__(self) -> None:
        self._data: dict[ProjectAllocationsId, Cashflow] = {}

    def get(self, project_id: ProjectAllocationsId) -> Cashflow:
        try:
            return deepcopy(self._data[project_id])
        except KeyError:
            raise NotFound

    def get_all(
        self, ids: list[ProjectAllocationsId] | None = None
    ) -> Sequence[Cashflow]:
        if ids is None:
            return [deepcopy(cashflow) for cashflow in self._data.values()]

        present_ids = set(self._data.keys()) & set(ids)
        return [deepcopy(self._data[project_id]) for project_id in present_ids]

    def add(self, cashflow: Cashflow) -> None:
        self._data[cashflow.project_id] = deepcopy(cashflow)
