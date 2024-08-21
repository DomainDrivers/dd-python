from itertools import chain

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.calendars import Calendars
from smartschedule.planning.chosen_resources import ChosenResources
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.resource_name import ResourceName
from smartschedule.shared.timeslot.time_slot import TimeSlot


class PlanChosenResources:
    def __init__(
        self,
        project_repository: ProjectRepository,
        availability_facade: AvailabilityFacade,
    ) -> None:
        self._project_repository = project_repository
        self._availability_facade = availability_facade

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        resources: set[ResourceName],
        time_boundaries: TimeSlot,
    ) -> None:
        project = self._project_repository.get(id=project_id)
        chosen_resources = ChosenResources(resources, time_boundaries)
        project.add_chosen_resources(chosen_resources)

    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        needed_resources = set(chain.from_iterable(stage.resources for stage in stages))
        project = self._project_repository.get(id=project_id)
        self.define_resources_within_dates(
            project_id, needed_resources, time_boundaries
        )
        # TODO: when availability is implemented
        needed_resources_calendars = Calendars.of()
        schedule = self._create_schedule_adjusting_to_calendars(
            needed_resources_calendars, *stages
        )
        project.add_schedule(schedule)

    def _create_schedule_adjusting_to_calendars(
        self, needed_resources_calendars: Calendars, *stages: Stage
    ) -> Schedule:
        return Schedule.based_on_chosen_resource_availability(
            needed_resources_calendars, list(stages)
        )
