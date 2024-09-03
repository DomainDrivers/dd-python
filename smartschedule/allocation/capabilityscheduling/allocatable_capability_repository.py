from datetime import datetime

from sqlalchemy import select, text

from smartschedule.allocation.capabilityscheduling.allocatable_capability import (
    AllocatableCapability,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class AllocatableCapabilityRepository(
    SQLAlchemyRepository[AllocatableCapability, AllocatableCapabilityId]
):
    def find_by_capability_within(
        self, name: str, type: str, from_: datetime, to: datetime
    ) -> list[AllocatableCapability]:
        stmt = text(
            """SELECT ac.*
            FROM allocatable_capabilities ac
            CROSS JOIN LATERAL
                jsonb_array_elements(ac.possible_capabilities -> 'capabilities') AS o(obj)
            WHERE
                o.obj ->> 'name' = :name
                AND o.obj ->> 'type' = :type
                AND ac.from_date <= :from_date
                AND ac.to_date >= :to_date
        """
        )
        params = {"name": name, "type": type, "from_date": from_, "to_date": to}
        result = self._session.execute(select(self._type).from_statement(stmt), params)
        return list(result.scalars().all())

    def find_by_resource_id_and_capability_and_time_slot(
        self,
        allocatable_resource_id: AllocatableResourceId,
        name: str,
        type: str,
        from_: datetime,
        to: datetime,
    ) -> AllocatableCapability | None:
        stmt = text(
            """SELECT ac.*
            FROM allocatable_capabilities ac
            CROSS JOIN LATERAL
                jsonb_array_elements(ac.possible_capabilities -> 'capabilities') AS o(obj)
            WHERE
                o.obj ->> 'name' = :name
                AND o.obj ->> 'type' = :type
                AND ac.resource_id = :resource_id
                AND ac.from_date <= :from_date
                AND ac.to_date >= :to_date
        """
        )
        params = {
            "resource_id": allocatable_resource_id.id,
            "name": name,
            "type": type,
            "from_date": from_,
            "to_date": to,
        }
        result = self._session.execute(select(self._type).from_statement(stmt), params)
        return result.scalar()

    def find_by_resource_id_and_time_slot(
        self,
        allocatable_resource_id: AllocatableResourceId,
        from_: datetime,
        to: datetime,
    ) -> list[AllocatableCapability]:
        stmt = select(self._type).filter(
            self._type.resource_id == allocatable_resource_id,
            self._type._from_date <= from_,
            self._type._to_date >= to,
        )
        return list(self._session.execute(stmt).scalars().all())
