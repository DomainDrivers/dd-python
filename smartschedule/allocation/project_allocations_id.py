from __future__ import annotations

from uuid import UUID, uuid4


class ProjectAllocationsId:
    def __init__(self, uuid: UUID) -> None:
        self._project_allocations_id = uuid

    @property
    def id(self) -> UUID:
        return self._project_allocations_id

    @staticmethod
    def new_one() -> ProjectAllocationsId:
        return ProjectAllocationsId(uuid4())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectAllocationsId):
            return False
        return self._project_allocations_id == other._project_allocations_id

    def __hash__(self) -> int:
        return hash(self._project_allocations_id)

    def __repr__(self) -> str:
        return f"ProjectAllocationsId(UUID(hex='{self._project_allocations_id}'))"

    def __str__(self) -> str:
        return str(self._project_allocations_id)
