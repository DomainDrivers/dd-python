from __future__ import annotations

from dataclasses import dataclass

from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)


@dataclass(frozen=True)
class SimulatedCapabilities:
    capabilities: list[AvailableResourceCapability]

    def add(
        self, *new_capabilities: AvailableResourceCapability
    ) -> SimulatedCapabilities:
        new_availabilities = self.capabilities + list(new_capabilities)
        return SimulatedCapabilities(new_availabilities)
