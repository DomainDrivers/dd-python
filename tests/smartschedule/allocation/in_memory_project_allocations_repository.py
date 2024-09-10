from datetime import datetime

from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.shared.repository import NotFound


class InMemoryProjectAllocationsRepository(ProjectAllocationsRepository):
    def __init__(self) -> None:
        self._data: dict[ProjectAllocationsId, ProjectAllocations] = {}

    def get(self, id: ProjectAllocationsId) -> ProjectAllocations:
        try:
            return self._data[id]
        except KeyError:
            raise NotFound

    def get_all(
        self, ids: list[ProjectAllocationsId] | None = None
    ) -> list[ProjectAllocations]:
        if ids is None:
            return list(self._data.values())
        return [self._data[id] for id in ids]

    def add(self, model: ProjectAllocations) -> None:
        self._data[model.project_id] = model

    def find_all_containing_date(self, when: datetime) -> list[ProjectAllocations]:
        return [
            project
            for project in self._data.values()
            if project.time_slot.from_ <= when and project.time_slot.to > when
        ]
