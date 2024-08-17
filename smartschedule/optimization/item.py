from dataclasses import dataclass

from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.optimization.total_weight import TotalWeight


@dataclass(frozen=True)
class Item[T: CapacityDimension]:
    name: str
    value: float
    total_weight: TotalWeight[T]

    def is_weight_zero(self) -> bool:
        return len(self.total_weight.components) == 0

    def __hash__(self) -> int:
        return hash((self.name, self.value))
