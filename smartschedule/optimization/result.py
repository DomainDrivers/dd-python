from dataclasses import dataclass

from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.optimization.item import Item


@dataclass(frozen=True)
class Result[T: CapacityDimension]:
    profit: float
    chosen_items: list[Item[T]]
    item_to_capacities: dict[Item[T], set[CapacityDimension]]

    def __str__(self) -> str:
        return f"Result{{profit={self.profit}, chosen_items={self.chosen_items}}}"
