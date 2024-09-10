from copy import deepcopy
from typing import Sequence

from smartschedule.planning.project import Project
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.shared.repository import NotFound


class InMemoryProjectRepository(ProjectRepository):
    def __init__(self) -> None:
        self._data: dict[ProjectId, Project] = {}

    def get(self, id: ProjectId) -> Project:
        try:
            return self._data[id]
        except KeyError:
            raise NotFound

    def get_all(self, ids: list[ProjectId] | None = None) -> Sequence[Project]:
        if ids is None:
            return [project for project in self._data.values()]

        present_ids = set(self._data.keys()) & set(ids)
        return [self._data[id] for id in present_ids]

    def save(self, model: Project) -> None:
        self._data[model.id] = deepcopy(model)
