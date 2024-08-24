from smartschedule.resource.device.device import Device
from smartschedule.resource.device.device_id import DeviceId
from smartschedule.resource.device.device_repository import DeviceRepository
from smartschedule.resource.device.device_summary import DeviceSummay
from smartschedule.shared.capability.capability import Capability


class DeviceFacade:
    def __init__(self, device_repository: DeviceRepository) -> None:
        self._device_repository = device_repository

    def find_device(self, device_id: DeviceId) -> DeviceSummay:
        return self._device_repository.find_summary(device_id)

    def find_all_capabilities(self) -> list[Capability]:
        return self._device_repository.find_all_capabilities()

    def create_device(self, model: str, assets: set[Capability]) -> DeviceId:
        device_id = DeviceId.new_one()
        device = Device(device_id, model, assets)
        self._device_repository.add(device)
        return device.id
