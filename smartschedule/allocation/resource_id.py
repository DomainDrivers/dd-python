from __future__ import annotations

from uuid import UUID, uuid4


class ResourceId:
    def __init__(self, uuid: UUID) -> None:
        self._resource_id = uuid

    @property
    def id(self) -> UUID:
        return self._resource_id

    @staticmethod
    def new_one() -> ResourceId:
        return ResourceId(uuid4())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ResourceId):
            return False
        return self._resource_id == other._resource_id

    def __hash__(self) -> int:
        return hash(self._resource_id)

    def __repr__(self) -> str:
        return f"ResourceId(UUID(hex='{self._resource_id}'))"

    def __str__(self) -> str:
        return str(self._resource_id)
