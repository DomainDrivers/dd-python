from __future__ import annotations

import functools
from dataclasses import dataclass
from decimal import Decimal


@functools.total_ordering
@dataclass(init=False, unsafe_hash=True)
class Earnings:
    _earnings: Decimal

    def __init__(self, value: Decimal | int) -> None:
        self._earnings = Decimal(value)

    def to_decimal(self) -> Decimal:
        return self._earnings

    def __gt__(self, other: Earnings) -> bool:
        return self._earnings > other._earnings
