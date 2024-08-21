from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class ProjectAllocationsRepository(
    SQLAlchemyRepository[ProjectAllocations, ProjectAllocationsId]
):
    pass
