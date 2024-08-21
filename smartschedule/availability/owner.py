from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Owner:
    owner: UUID | None

    @staticmethod
    def none() -> Owner:
        return Owner(None)

    @staticmethod
    def new_one() -> Owner:
        return Owner(uuid4())
