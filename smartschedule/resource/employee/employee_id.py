from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)


@dataclass(frozen=True)
class EmployeeId:
    employee_id: UUID

    @staticmethod
    def new_one() -> EmployeeId:
        return EmployeeId(uuid4())

    @property
    def id(self) -> UUID:
        return self.employee_id

    def to_allocatable_resource_id(self) -> AllocatableResourceId:
        return AllocatableResourceId(self.employee_id)
