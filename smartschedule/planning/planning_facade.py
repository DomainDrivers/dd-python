from datetime import date, datetime, timedelta

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.capabilities_demanded import CapabilitiesDemanded
from smartschedule.planning.critical_stage_planned import CriticalStagePlanned
from smartschedule.planning.demands import Demands
from smartschedule.planning.demands_per_stage import DemandsPerStage
from smartschedule.planning.parallelization.duration_calculator import (
    calculate_duration,
)
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.parallelization.stage_parallelization import (
    StageParallelization,
)
from smartschedule.planning.plan_chosen_resources import PlanChosenResources
from smartschedule.planning.project import Project
from smartschedule.planning.project_card import ProjectCard
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.events_publisher import EventsPublisher
from smartschedule.shared.timeslot.time_slot import TimeSlot


class PlanningFacade:
    def __init__(
        self,
        project_repository: ProjectRepository,
        stage_parallelization: StageParallelization,
        plan_chosen_resources_service: PlanChosenResources,
        evens_publisher: EventsPublisher,
    ) -> None:
        self._project_repository = project_repository
        self._stage_parallelization = stage_parallelization
        self._plan_chosen_resources_service = plan_chosen_resources_service
        self._events_publisher = evens_publisher

    def add_new_project(self, name: str, *stages: Stage) -> ProjectId:
        parallelized_stages = self._stage_parallelization.of(set(stages))
        project = Project(name, parallelized_stages)
        self._project_repository.add(project)
        return project.id

    def add_new_project_with_parallelized_stages(
        self, name: str, parallelized_stages: ParallelStagesList
    ) -> ProjectId:
        project = Project(name, parallelized_stages)
        self._project_repository.add(project)
        return project.id

    def add_demands(self, project_id: ProjectId, demands: Demands) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_demands(demands)
        event = CapabilitiesDemanded(project_id, project.all_demands, datetime.now())
        self._events_publisher.publish(event)

    def define_demands_per_stage(
        self, project_id: ProjectId, demands_per_stage: DemandsPerStage
    ) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_demands_per_stage(demands_per_stage)
        event = CapabilitiesDemanded(project_id, project.all_demands, datetime.now())
        self._events_publisher.publish(event)

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        chosen_resources: set[ResourceId],
        time_boundaries: TimeSlot,
    ) -> None:
        self._plan_chosen_resources_service.define_resources_within_dates(
            project_id, chosen_resources, time_boundaries
        )

    def define_project_stages(self, project_id: ProjectId, *stages: Stage) -> None:
        project = self._project_repository.get(id=project_id)
        parallelized_stages = self._stage_parallelization.of(set(stages))
        project.parallelized_stages = parallelized_stages

    def define_start_date(self, project_id: ProjectId, start_date: date) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule_by_start_date(start_date)

    def define_manual_schedule(self, project_id: ProjectId, schedule: Schedule) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule(schedule)

    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        self._plan_chosen_resources_service.adjust_stages_to_resource_availability(
            project_id, time_boundaries, *stages
        )

    def plan_critical_stage_with_resource(
        self,
        project_id: ProjectId,
        critical_stage: Stage,
        resource_id: ResourceId,
        stage_time_slot: TimeSlot,
    ) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule_by_critical_stage(critical_stage, stage_time_slot)
        event = CriticalStagePlanned(
            project_id, stage_time_slot, resource_id, datetime.now()
        )
        self._events_publisher.publish(event)

    def plan_critical_stage(
        self, project_id: ProjectId, critical_stage: Stage, stage_time_slot: TimeSlot
    ) -> None:
        project = self._project_repository.get(id=project_id)
        project.add_schedule_by_critical_stage(critical_stage, stage_time_slot)
        event = CriticalStagePlanned(project_id, stage_time_slot, None, datetime.now())
        self._events_publisher.publish(event)

    def duration_of(self, *stages: Stage) -> timedelta:
        return calculate_duration(stages)

    def load(self, project_id: ProjectId) -> ProjectCard:
        project = self._project_repository.get(id=project_id)
        return self._to_project_card(project)

    def load_all(self, *project_ids: ProjectId) -> list[ProjectCard]:
        ids = None if not project_ids else list(project_ids)
        projects = self._project_repository.get_all(ids=ids)
        return [self._to_project_card(project) for project in projects]

    def _to_project_card(self, project: Project) -> ProjectCard:
        return ProjectCard(
            project_id=project.id,
            name=project.name,
            parallelized_stages=project.parallelized_stages,
            demands=project.all_demands,
            schedule=project.schedule,
            demands_per_stage=project.demands_per_stage,
            needed_resources=project.chosen_resources,
        )
