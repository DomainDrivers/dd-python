from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class AllocatableResourceId:
    _resource_id: UUID

    @property
    def id(self) -> UUID:
        return self._resource_id

    @staticmethod
    def new_one() -> AllocatableResourceId:
        return AllocatableResourceId(uuid4())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AllocatableResourceId):
            return False
        return self._resource_id == other._resource_id
