from __future__ import annotations

from dataclasses import dataclass

from smartschedule.optimization.capacity_dimension import CapacityDimension


@dataclass(frozen=True)
class TotalCapacity:
    capacities: list[CapacityDimension]

    @classmethod
    def of(cls, *capacities: CapacityDimension) -> TotalCapacity:
        return TotalCapacity(list(capacities))

    @classmethod
    def zero(cls) -> TotalCapacity:
        return TotalCapacity([])

    def add(self, capacities: list[CapacityDimension]) -> TotalCapacity:
        return TotalCapacity(self.capacities + capacities)

    def __len__(self) -> int:
        return len(self.capacities)
