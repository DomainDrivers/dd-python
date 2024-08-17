from __future__ import annotations

from dataclasses import dataclass

from smartschedule.allocation.allocated_capability import AllocatedCapability
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
        self, to_remove: AllocatedCapability, time_slot: TimeSlot
    ) -> Allocations:
        allocated_resource = self.find(to_remove, time_slot)
        if allocated_resource is None:
            return self
        difference = allocated_resource.time_slot.leftover_after_removing_common_with(
            time_slot
        )
        leftovers: set[AllocatedCapability] = {
            AllocatedCapability(
                allocated_resource.resource_id, allocated_resource.capability, leftover
            )
            for leftover in difference
            if leftover.within(to_remove.time_slot)
        }

        return Allocations(all=self.all.difference({to_remove}).union(leftovers))

    def find(
        self, capability: AllocatedCapability, for_slot: TimeSlot
    ) -> AllocatedCapability | None:
        return next(
            (allocation for allocation in self.all if allocation == capability), None
        )
