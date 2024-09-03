from __future__ import annotations

from dataclasses import dataclass

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class Allocations:
    all: set[AllocatedCapability]

    @staticmethod
    def none() -> Allocations:
        return Allocations(all=set())

    def add(self, allocated_capability: AllocatedCapability) -> Allocations:
        return Allocations(all=self.all.union({allocated_capability}))

    def remove(
        self, to_remove: AllocatableCapabilityId, time_slot: TimeSlot
    ) -> Allocations:
        allocated_capability = self.find(to_remove)
        if allocated_capability is None:
            return self
        return self._remove_from_slot(allocated_capability, time_slot)

    def _remove_from_slot(
        self, allocated_capability: AllocatedCapability, time_slot: TimeSlot
    ) -> Allocations:
        difference = allocated_capability.time_slot.leftover_after_removing_common_with(
            time_slot
        )
        leftovers: set[AllocatedCapability] = {
            AllocatedCapability(
                allocated_capability.allocated_capability_id,
                allocated_capability.capability,
                leftover,
            )
            for leftover in difference
            if leftover.within(allocated_capability.time_slot)
        }

        return Allocations(
            all=self.all.difference({allocated_capability}).union(leftovers)
        )

    def find(
        self, allocated_capability_id: AllocatableCapabilityId
    ) -> AllocatedCapability | None:
        return next(
            (
                allocation
                for allocation in self.all
                if allocation.allocated_capability_id == allocated_capability_id
            ),
            None,
        )
