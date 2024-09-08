from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.availability.calendar import Calendar
from smartschedule.planning.critical_stage_planned import CriticalStagePlanned
from smartschedule.risk.risk_push_notification import RiskPushNotification
from smartschedule.shared.event_bus import EventBus
from smartschedule.shared.timeslot.time_slot import TimeSlot


@EventBus.has_event_handlers
class VerifyCriticalResourceAvailableDuringPlanning:
    def __init__(
        self,
        availability_facade: AvailabilityFacade,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._availability_facade = availability_facade
        self._risk_push_notification = risk_push_notification

    @EventBus.async_event_handler
    def handle(self, event: CriticalStagePlanned) -> None:
        if event.critical_resource_id is None:
            return

        calendar = self._availability_facade.load_calendar(
            event.critical_resource_id, event.stage_time_slot
        )
        if not self._resource_is_available(event.stage_time_slot, calendar):
            self._risk_push_notification.notify_about_critical_resource_not_available(
                event.project_id, event.critical_resource_id, event.stage_time_slot
            )

    def _resource_is_available(self, time_slot: TimeSlot, calendar: Calendar) -> bool:
        return time_slot in calendar.available_slots()
