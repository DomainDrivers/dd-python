from smartschedule.planning.project import Project
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class ProjectRepository(SQLAlchemyRepository[Project, ProjectId]):
    pass
