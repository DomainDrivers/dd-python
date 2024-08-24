import itertools

from smartschedule.resource.device.device import Device
from smartschedule.resource.device.device_id import DeviceId
from smartschedule.resource.device.device_summary import DeviceSummay
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class DeviceRepository(SQLAlchemyRepository[Device, DeviceId]):
    def find_summary(self, device_id: DeviceId) -> DeviceSummay:
        device = self.get(device_id)
        return DeviceSummay(device.id, device.model, device.capabilities)

    def find_all_capabilities(self) -> list[Capability]:
        devices = self.get_all()
        capabilities_sets = [device.capabilities for device in devices]
        return list(itertools.chain(*capabilities_sets))
