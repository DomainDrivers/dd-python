import abc
from typing import Sequence

from smartschedule.planning.project import Project
from smartschedule.planning.project_id import ProjectId


class ProjectRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, id: ProjectId) -> Project:
        pass

    @abc.abstractmethod
    def get_all(self, ids: list[ProjectId] | None = None) -> Sequence[Project]:
        pass

    @abc.abstractmethod
    def add(self, model: Project) -> None:
        pass
