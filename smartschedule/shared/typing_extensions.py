from typing import Any, Protocol, TypeAlias


class SupportsDunderLT(Protocol):
    def __lt__(self, __other: Any) -> bool: ...


class SupportsDunderGT(Protocol):
    def __gt__(self, __other: Any) -> bool: ...


Comparable = SupportsDunderLT | SupportsDunderGT

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
