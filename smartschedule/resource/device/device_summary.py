from dataclasses import dataclass

from smartschedule.resource.device.device_id import DeviceId
from smartschedule.shared.capability.capability import Capability


@dataclass(frozen=True)
class DeviceSummay:
    id: DeviceId
    model: str
    assets: set[Capability]
