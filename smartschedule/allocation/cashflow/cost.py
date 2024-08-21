from dataclasses import dataclass
from decimal import Decimal


@dataclass(init=False, unsafe_hash=True)
class Cost:
    _cost: Decimal

    def __init__(self, cost: Decimal | int) -> None:
        self._cost = Decimal(cost)

    @property
    def value(self) -> Decimal:
        return self._cost
