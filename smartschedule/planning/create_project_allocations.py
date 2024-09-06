from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository


class CreateProjectAllocations:
    def __init__(
        self, allocation_facade: AllocationFacade, project_repository: ProjectRepository
    ) -> None:
        self._allocation_facade = allocation_facade
        self._project_repository = project_repository

    # can react to ScheduleCalculated event
    def create_project_allocations(self, project_id: ProjectId) -> None:
        project = self._project_repository.get(project_id)
        schedule = project.schedule  # noqa: F841
        # for each stage in schedule
        #     create allocation
        #     allocate chosen resources (or find equivalents)
        #     start risk analysis
