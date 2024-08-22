from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Owner:
    owner: UUID

    @staticmethod
    def none() -> Owner:
        return Owner(UUID(int=0))

    @staticmethod
    def new_one() -> Owner:
        return Owner(uuid4())

    def by_none(self) -> bool:
        return self.owner == UUID(int=0)

    @property
    def id(self) -> UUID:
        return self.owner
