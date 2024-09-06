from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.resource.device.device import Device
from smartschedule.resource.device.device_id import DeviceId
from smartschedule.resource.device.device_repository import DeviceRepository
from smartschedule.resource.device.device_summary import DeviceSummay
from smartschedule.resource.device.schedule_device_capabilities import (
    ScheduleDeviceCapabilities,
)
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class DeviceFacade:
    def __init__(
        self,
        device_repository: DeviceRepository,
        schedule_device_capabilities: ScheduleDeviceCapabilities,
    ) -> None:
        self._device_repository = device_repository
        self._schedule_device_capabilities = schedule_device_capabilities

    def find_device(self, device_id: DeviceId) -> DeviceSummay:
        return self._device_repository.find_summary(device_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self._device_repository.find_all_capabilities()

    def create_device(self, model: str, assets: set[Capability]) -> DeviceId:
        device_id = DeviceId.new_one()
        device = Device(device_id, model, assets)
        self._device_repository.add(device)
        return device.id

    def schedule_capabilities(
        self, device_id: DeviceId, time_slot: TimeSlot
    ) -> list[AllocatableCapabilityId]:
        return self._schedule_device_capabilities.setup_device_capabilities(
            device_id, time_slot
        )
