from smartschedule.resource.device.device_facade import DeviceFacade
from smartschedule.shared.capability.capability import Capability


class TestCreatingDevice:
    def test_creates_and_loads_devices(self, device_facade: DeviceFacade) -> None:
        device_id = device_facade.create_device(
            "super-excavator-1000", Capability.assets("BULLDOZER", "EXCAVATOR")
        )

        loaded = device_facade.find_device(device_id)

        assert loaded.assets == Capability.assets("BULLDOZER", "EXCAVATOR")
        assert loaded.model == "super-excavator-1000"

    def test_find_all_capabilities(self, device_facade: DeviceFacade) -> None:
        device_facade.create_device(
            "super-excavator-1000", Capability.assets("SMALL-EXCAVATOR", "BULLDOZER")
        )
        device_facade.create_device(
            "super-excavator-1000",
            Capability.assets("MEDIUM-EXCAVATOR", "UBER-BULLDOZER"),
        )
        device_facade.create_device(
            "super-excavator-1000", Capability.assets("BIG-EXCAVATOR")
        )

        loaded = device_facade.find_all_capabilities()

        assert set(loaded) == {
            Capability.asset("SMALL-EXCAVATOR"),
            Capability.asset("BULLDOZER"),
            Capability.asset("MEDIUM-EXCAVATOR"),
            Capability.asset("UBER-BULLDOZER"),
            Capability.asset("BIG-EXCAVATOR"),
        }
