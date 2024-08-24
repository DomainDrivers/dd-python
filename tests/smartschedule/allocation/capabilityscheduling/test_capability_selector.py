from typing import Final

from smartschedule.allocation.capabilityscheduling.capability_selector import (
    CapabilitySelector,
)
from smartschedule.shared.capability.capability import Capability


class TestCapabilitySelector:
    RUST: Final = Capability.skill("RUST")
    BEING_AN_ADMIN: Final = Capability.permission("ADMIN")
    JAVA: Final = Capability.skill("JAVA")

    def test_allocatable_resources_can_perform_only_one_of_present_capabilities(
        self,
    ) -> None:
        admin_or_rust = CapabilitySelector.can_perform_one_of(
            {self.RUST, self.BEING_AN_ADMIN}
        )

        assert admin_or_rust.can_perform(self.BEING_AN_ADMIN)
        assert admin_or_rust.can_perform(self.RUST)
        assert not admin_or_rust.can_perform(self.BEING_AN_ADMIN, self.RUST)
        assert not admin_or_rust.can_perform(Capability.skill("JAVA"))
        assert not admin_or_rust.can_perform(Capability.permission("LAWYER"))

    def test_allocatable_resource_can_perform_simultanous_capabilities(self) -> None:
        admin_and_rust = CapabilitySelector.can_perform_all_at_the_time(
            {self.BEING_AN_ADMIN, self.RUST}
        )

        assert admin_and_rust.can_perform(self.BEING_AN_ADMIN)
        assert admin_and_rust.can_perform(self.RUST)
        assert admin_and_rust.can_perform(self.BEING_AN_ADMIN, self.RUST)
        assert not admin_and_rust.can_perform(self.RUST, self.BEING_AN_ADMIN, self.JAVA)
        assert not admin_and_rust.can_perform(self.JAVA)
        assert not admin_and_rust.can_perform(Capability.permission("LAWYER"))
