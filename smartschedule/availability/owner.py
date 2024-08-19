from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Owner:
    owner: UUID | None

    @staticmethod
    def none() -> Owner:
        return Owner(None)
