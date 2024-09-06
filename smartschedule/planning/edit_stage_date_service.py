from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.shared.timeslot.time_slot import TimeSlot


class EditStageDateService:
    def __init__(
        self, allocation_facade: AllocationFacade, project_repository: ProjectRepository
    ) -> None:
        self._allocation_facade = allocation_facade
        self._project_repository = project_repository

    def edit_stage_date(
        self, project_id: ProjectId, stage: Stage, time_slot: TimeSlot
    ) -> None:
        project = self._project_repository.get(project_id)
        schedule = project.schedule  # noqa: F841
        # redefine schedule
        # for each stage in schedule
        #     recreate allocation
        #     reallocate chosen resources (or find equivalents)
        #     start risk analysis
