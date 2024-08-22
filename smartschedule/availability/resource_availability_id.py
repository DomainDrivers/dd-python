from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ResourceAvailabilityId:
    id: UUID

    @staticmethod
    def none() -> ResourceAvailabilityId:
        return ResourceAvailabilityId(UUID(int=0))

    @staticmethod
    def new_one() -> ResourceAvailabilityId:
        return ResourceAvailabilityId(uuid4())

    @staticmethod
    def from_str(value: str) -> ResourceAvailabilityId:
        return ResourceAvailabilityId(UUID(hex=value))
