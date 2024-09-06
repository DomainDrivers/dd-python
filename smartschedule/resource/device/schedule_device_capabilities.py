from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.capability_scheduler import (
    CapabilityScheduler,
)
from smartschedule.resource.device.device_id import DeviceId
from smartschedule.resource.device.device_repository import DeviceRepository
from smartschedule.shared.capability_selector import CapabilitySelector
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ScheduleDeviceCapabilities:
    def __init__(
        self,
        device_repository: DeviceRepository,
        capability_scheduler: CapabilityScheduler,
    ) -> None:
        self._device_repository = device_repository
        self._capability_scheduler = capability_scheduler

    def setup_device_capabilities(
        self, device_id: DeviceId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        summary = self._device_repository.find_summary(device_id)
        return self._capability_scheduler.schedule_resource_capabilities_for_period(
            device_id.to_allocatable_resource_id(),
            [CapabilitySelector.can_perform_all_at_the_time(summary.assets)],
            time_slot,
        )
