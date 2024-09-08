from datetime import datetime
from itertools import chain

from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.calendars import Calendars
from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.chosen_resources import ChosenResources
from smartschedule.planning.needed_resource_chosen import NeededResourcesChosen
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.events_publisher import EventsPublisher
from smartschedule.shared.timeslot.time_slot import TimeSlot


class PlanChosenResources:
    def __init__(
        self,
        project_repository: ProjectRepository,
        availability_facade: AvailabilityFacade,
        events_publisher: EventsPublisher,
    ) -> None:
        self._project_repository = project_repository
        self._availability_facade = availability_facade
        self._events_publisher = events_publisher

    def define_resources_within_dates(
        self,
        project_id: ProjectId,
        resources: set[ResourceId],
        time_boundaries: TimeSlot,
    ) -> None:
        project = self._project_repository.get(id=project_id)
        chosen_resources = ChosenResources(resources, time_boundaries)
        project.add_chosen_resources(chosen_resources)
        event = NeededResourcesChosen(
            project_id, resources, time_boundaries, datetime.now()
        )
        self._events_publisher.publish(event)

    def adjust_stages_to_resource_availability(
        self, project_id: ProjectId, time_boundaries: TimeSlot, *stages: Stage
    ) -> None:
        needed_resources = set(chain.from_iterable(stage.resources for stage in stages))
        project = self._project_repository.get(id=project_id)
        self.define_resources_within_dates(
            project_id, needed_resources, time_boundaries
        )
        needed_resources_calendars = self._availability_facade.load_calendars(
            needed_resources, time_boundaries
        )
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
