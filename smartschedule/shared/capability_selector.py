from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto

from smartschedule.shared.capability.capability import Capability


class SelectingPolicy(StrEnum):
    ALL_SIMULTANEOUSLY = auto()
    ONE_OF_ALL = auto()


@dataclass(frozen=True)
class CapabilitySelector:
    capabilities: frozenset[Capability]
    selecting_policy: SelectingPolicy

    @staticmethod
    def can_perform_all_at_the_time(
        capabilities: set[Capability],
    ) -> CapabilitySelector:
        return CapabilitySelector(
            frozenset(capabilities), SelectingPolicy.ALL_SIMULTANEOUSLY
        )

    @staticmethod
    def can_perform_one_of(capabilities: set[Capability]) -> CapabilitySelector:
        return CapabilitySelector(frozenset(capabilities), SelectingPolicy.ONE_OF_ALL)

    @staticmethod
    def can_just_perform(capability: Capability) -> CapabilitySelector:
        return CapabilitySelector(frozenset({capability}), SelectingPolicy.ONE_OF_ALL)

    def can_perform(self, *capabilities: Capability) -> bool:
        if len(capabilities) == 1:
            return capabilities[0] in self.capabilities

        return (
            self.selecting_policy == SelectingPolicy.ALL_SIMULTANEOUSLY
            and self.capabilities.issuperset(set(capabilities))
        )
