from smartschedule.planning.project import Project
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class SqlAlchemyProjectRepository(
    SQLAlchemyRepository[Project, ProjectId], ProjectRepository
):
    pass
