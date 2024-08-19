from __future__ import annotations

from dataclasses import dataclass

from smartschedule.shared.capability.capability import Capability


@dataclass(frozen=True)
class Demand:
    capability: Capability

    @staticmethod
    def for_(capability: Capability) -> Demand:
        return Demand(capability)
