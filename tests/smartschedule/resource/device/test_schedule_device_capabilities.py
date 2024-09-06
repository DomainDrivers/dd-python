from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.resource.device.device_facade import DeviceFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestScheduleDeviceCapabilities:
    def test_can_setup_capabilities_according_to_policy(
        self, device_facade: DeviceFacade, capability_finder: CapabilityFinder
    ) -> None:
        device_id = device_facade.create_device(
            "super-bulldozer-3000", Capability.assets("EXCAVATOR", "BULLDOZER")
        )

        one_day = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
        allocations = device_facade.schedule_capabilities(device_id, one_day)

        loaded = capability_finder.find_by_id(allocations)
        assert len(loaded.all) == len(allocations)
