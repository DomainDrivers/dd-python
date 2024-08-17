from __future__ import annotations

from decimal import Decimal

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demands import Demands
from smartschedule.shared.timeslot.time_slot import TimeSlot


class Project:
    def __init__(self, demands: Demands, earnings: Decimal) -> None:
        self._earnings = earnings
        self._demands = demands
        self._allocations = Allocations.none()

    @property
    def missing_demands(self) -> Demands:
        return self._demands.missing_demands(self._allocations)

    @property
    def earnings(self) -> Decimal:
        return self._earnings

    def remove(
        self, capability: AllocatedCapability, for_slot: TimeSlot
    ) -> AllocatedCapability | None:
        to_remove = self._allocations.find(capability, for_slot)
        if not to_remove:
            return None
        self._allocations = self._allocations.remove(to_remove, for_slot)
        return to_remove

    def add(self, allocated_capability: AllocatedCapability) -> Project:
        self._allocations = self._allocations.add(allocated_capability)
        return self
