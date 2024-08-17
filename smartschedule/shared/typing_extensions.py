from typing import Any, Protocol


class SupportsDunderLT(Protocol):
    def __lt__(self, __other: Any) -> bool: ...


class SupportsDunderGT(Protocol):
    def __gt__(self, __other: Any) -> bool: ...


Comparable = SupportsDunderLT | SupportsDunderGT
