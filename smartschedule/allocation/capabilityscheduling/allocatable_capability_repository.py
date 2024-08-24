from datetime import datetime

from sqlalchemy import select

from smartschedule.allocation.capabilityscheduling.allocatable_capability import (
    AllocatableCapability,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class AllocatableCapabilityRepository(
    SQLAlchemyRepository[AllocatableCapability, AllocatableCapabilityId]
):
    def find_by_capability_within(
        self, name: str, type: str, from_: datetime, to: datetime
    ) -> list[AllocatableCapability]:
        stmt = select(self._type).filter(
            self._type.capability["name"].astext == name,
            self._type.capability["type"].astext == type,
            self._type._from_date <= from_,
            self._type._to_date >= to,
        )
        return list(self._session.execute(stmt).scalars().all())
