from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.needed_resource_chosen import NeededResourcesChosen
from smartschedule.planning.project_id import ProjectId
from smartschedule.risk.risk_push_notification import RiskPushNotification
from smartschedule.shared.event_bus import EventBus
from smartschedule.shared.timeslot.time_slot import TimeSlot


@EventBus.has_event_handlers
class VerifyNeededResourcesAvailableInTimeSlot:
    def __init__(
        self,
        availability_facade: AvailabilityFacade,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._availability_facade = availability_facade
        self._risk_push_notification = risk_push_notification

    @EventBus.async_event_handler
    def handle(self, event: NeededResourcesChosen) -> None:
        self._notify_about_not_available_resources(
            event.needed_resources, event.time_slot, event.project_id
        )

    def _notify_about_not_available_resources(
        self, resource_ids: set[ResourceId], time_slot: TimeSlot, project_id: ProjectId
    ) -> None:
        not_available: set[ResourceId] = set()
        calendars = self._availability_facade.load_calendars(resource_ids, time_slot)
        for resource_id in resource_ids:
            available_slots = calendars.get(resource_id).available_slots()
            if not any(time_slot.within(slot) for slot in available_slots):
                not_available.add(resource_id)
        if len(not_available) > 0:
            self._risk_push_notification.notify_about_resources_not_available(
                project_id, not_available
            )
