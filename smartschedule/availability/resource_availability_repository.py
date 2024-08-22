from collections import deque
from typing import Any, Sequence

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Table,
    UniqueConstraint,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from smartschedule.availability.blockade import Blockade
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability import ResourceAvailability
from smartschedule.availability.resource_availability_id import ResourceAvailabilityId
from smartschedule.availability.resource_grouped_availability import (
    ResourceGroupedAvailability,
)
from smartschedule.shared.sqlalchemy_extensions import registry
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ResourceAvailabilityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_new(
        self, resource_availability: ResourceAvailability | ResourceGroupedAvailability
    ) -> None:
        match resource_availability:
            case ResourceAvailability():
                self._save([resource_availability])
            case ResourceGroupedAvailability():
                self._save(resource_availability.resource_availabilities)

    def _save(self, resource_availabilities: Sequence[ResourceAvailability]) -> None:
        self._session.execute(
            insert(availabilities),
            [
                {
                    "id": ra.id.id,
                    "resource_id": ra.resource_id.id,
                    "resource_parent_id": ra.parent_id.id,
                    "version": ra.version,
                    "from_date": ra.segment.from_,
                    "to_date": ra.segment.to,
                    "taken_by": ra.blocked_by().id,
                    "disabled": ra.is_disabled(),
                }
                for ra in resource_availabilities
            ],
        )

    def load_by_id(
        self, resource_availability_id: ResourceAvailabilityId
    ) -> ResourceAvailability:
        stmt = select(availabilities).filter(
            availabilities.c.id == resource_availability_id.id
        )
        row = self._session.execute(stmt).one()
        return _to_resource_availability(row)

    def load_all_within_slot(
        self, resource_id: ResourceAvailabilityId, slot: TimeSlot
    ) -> list[ResourceAvailability]:
        stmt = select(availabilities).filter(
            availabilities.c.resource_id == resource_id.id,
            availabilities.c.from_date >= slot.from_,
            availabilities.c.to_date <= slot.to,
        )
        return [_to_resource_availability(row) for row in self._session.execute(stmt)]

    def load_all_by_parent_id_within_slot(
        self, parent_id: ResourceAvailabilityId, slot: TimeSlot
    ) -> list[ResourceAvailability]:
        stmt = select(availabilities).filter(
            availabilities.c.resource_parent_id == parent_id.id,
            availabilities.c.from_date >= slot.from_,
            availabilities.c.to_date <= slot.to,
        )
        return [_to_resource_availability(row) for row in self._session.execute(stmt)]

    def save_checking_version(
        self,
        resource_availability: ResourceAvailability
        | ResourceGroupedAvailability
        | list[ResourceAvailability],
    ) -> bool:
        resource_availabilities: list[ResourceAvailability]

        match resource_availability:
            case ResourceAvailability():
                resource_availabilities = [resource_availability]
            case ResourceGroupedAvailability():
                resource_availabilities = resource_availability.resource_availabilities
            case list():
                resource_availabilities = resource_availability

        results: deque[bool] = deque()
        for ra in resource_availabilities:
            id = ra.id.id
            version = ra.version
            stmt = (
                update(availabilities)
                .where(availabilities.c.id == id, availabilities.c.version == version)
                .values(
                    version=version + 1,
                    taken_by=ra.blocked_by().id,
                    disabled=ra.is_disabled(),
                )
            )
            result = self._session.execute(stmt)
            results.append(result.rowcount == 1)

        return all(results)

    def load_availabilities_of_random_resources_within(
        self, normalized: TimeSlot, *resource_ids: ResourceAvailabilityId
    ) -> ResourceGroupedAvailability:
        available_resources = (
            select(availabilities.c.resource_id)
            .filter(
                availabilities.c.resource_id.in_(
                    [resouce_id.id for resouce_id in resource_ids]
                ),
                availabilities.c.taken_by == Owner.none().id,
                availabilities.c.from_date >= normalized.from_,
                availabilities.c.to_date <= normalized.to,
            )
            .group_by(availabilities.c.resource_id)
            .cte()
        )
        random_resource = (
            select(available_resources.c.resource_id)
            .order_by(func.random())
            .limit(1)
            .cte("random_resource")
        )
        stmt = select(availabilities).join(
            random_resource,
            availabilities.c.resource_id == random_resource.c.resource_id,
        )
        rows = self._session.execute(stmt)
        return ResourceGroupedAvailability(
            [_to_resource_availability(row) for row in rows]
        )


availabilities = Table(
    "availabilities",
    registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("resource_id", UUID(as_uuid=True), nullable=False),
    Column("resource_parent_id", UUID(as_uuid=True)),
    Column("version", Integer, nullable=False),
    Column("from_date", DateTime(timezone=True), nullable=False),
    Column("to_date", DateTime(timezone=True), nullable=False),
    Column("taken_by", UUID(as_uuid=True), nullable=False),
    Column("disabled", Boolean, nullable=False),
    UniqueConstraint("resource_id", "from_date", "to_date"),
)


def _to_resource_availability(row: Any) -> ResourceAvailability:
    owner = Owner(row[6])
    blockade = Blockade(owner, row[7])

    return ResourceAvailability(
        id=ResourceAvailabilityId(row[0]),
        resource_id=ResourceAvailabilityId(row[1]),
        segment=TimeSlot(row[4], row[5]),
        parent_id=ResourceAvailabilityId(row[2]),
        version=row[3],
        blockade=blockade,
    )
