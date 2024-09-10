import abc
from datetime import datetime
from typing import Sequence

from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId


class ProjectAllocationsRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: ProjectAllocationsId) -> ProjectAllocations:
        pass

    @abc.abstractmethod
    def get_all(
        self, ids: list[ProjectAllocationsId] | None = None
    ) -> Sequence[ProjectAllocations]:
        pass

    @abc.abstractmethod
    def add(self, model: ProjectAllocations) -> None:
        pass

    @abc.abstractmethod
    def find_all_containing_date(self, when: datetime) -> list[ProjectAllocations]:
        pass
