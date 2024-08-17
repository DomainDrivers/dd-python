from __future__ import annotations

from dataclasses import dataclass

from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.optimization.weight_dimension import WeightDimension


@dataclass(frozen=True)
class TotalWeight[T: CapacityDimension]:
    components: list[WeightDimension[T]]

    @classmethod
    def zero(cls) -> TotalWeight[T]:
        return TotalWeight[T]([])

    @classmethod
    def of(cls, *components: WeightDimension[T]) -> TotalWeight[T]:
        return TotalWeight(list(components))
