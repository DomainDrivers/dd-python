from __future__ import annotations

from datetime import datetime

from smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.shared.events_publisher import EventsPublisher


class PublishMissingDemandsService:
    def __init__(
        self,
        repository: ProjectAllocationsRepository,
        create_hourly_demands_service: CreateHourlyDemandsSummaryService,
        events_publisher: EventsPublisher,
    ) -> None:
        self._repository = repository
        self._create_hourly_demands_service = create_hourly_demands_service
        self._events_publisher = events_publisher

    # Run this hourly using some cron job, e.g. Celery Beat
    def publish(self) -> None:
        when = datetime.now()
        project_allocations = self._repository.find_all_containing_date(when)
        missing_demands = self._create_hourly_demands_service.create(
            project_allocations, when
        )
        # add metadata to the event
        # if needed call EventStore and translate multiple private events to a new published event
        self._events_publisher.publish(missing_demands)


class CreateHourlyDemandsSummaryService:
    def create(
        self, project_allocations: list[ProjectAllocations], when: datetime
    ) -> NotSatisfiedDemands:
        missing_demands = {
            pa.project_id: pa.missing_demands()
            for pa in project_allocations
            if pa.has_time_slot()
        }
        return NotSatisfiedDemands(missing_demands=missing_demands, occurred_at=when)
