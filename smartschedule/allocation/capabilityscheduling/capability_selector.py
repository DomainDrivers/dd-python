from __future__ import annotations

from smartschedule.shared.capability.capability import Capability


class CapabilitySelector:
    @staticmethod
    def can_perform_one_of(capabilities: set[Capability]) -> CapabilitySelector:
        return CapabilitySelector()

    @staticmethod
    def can_perform_all_at_the_time(
        being_an_admin: set[Capability],
    ) -> CapabilitySelector:
        return CapabilitySelector()

    def can_perform(self, *capabilities: Capability) -> bool:
        return False
