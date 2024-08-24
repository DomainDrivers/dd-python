from dataclasses import dataclass

from smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)


@dataclass(frozen=True)
class AllocatableCapabilitiesSummary:
    all: list[AllocatableCapabilitySummary]
