from dataclasses import dataclass
from decimal import Decimal

from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings


@dataclass(init=False, unsafe_hash=True)
class Income:
    _income: Decimal

    def __init__(self, value: Decimal | int) -> None:
        self._income = Decimal(value)

    def __sub__(self, other: Cost) -> Earnings:
        return Earnings(self._income - other.value)
