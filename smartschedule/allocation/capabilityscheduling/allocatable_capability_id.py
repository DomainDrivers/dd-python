from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from smartschedule.availability.resource_id import ResourceId


@dataclass(frozen=True)
class AllocatableCapabilityId:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    @staticmethod
    def new_one() -> AllocatableCapabilityId:
        return AllocatableCapabilityId(uuid4())

    @staticmethod
    def none() -> AllocatableCapabilityId:
        return AllocatableCapabilityId(UUID(int=0))

    def to_availability_resource_id(self) -> ResourceId:
        return ResourceId(self._id)

    @staticmethod
    def from_availability_resource_id(
        resource_id: ResourceId,
    ) -> AllocatableCapabilityId:
        return AllocatableCapabilityId(resource_id.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AllocatableCapabilityId):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"AllocatableCapabilityId(UUID(hex='{self._id}'))"

    def __str__(self) -> str:
        return str(self._id)
