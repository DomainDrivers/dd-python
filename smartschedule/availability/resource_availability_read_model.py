from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from smartschedule.availability.calendar import Calendar
from smartschedule.availability.calendars import Calendars
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_availability_repository import availabilities
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ResourceAvailabilityReadModel:
    def __init__(self, session: Session) -> None:
        self._session = session

    def load(self, resource_id: ResourceId, within: TimeSlot) -> Calendar:
        calendars = self.load_all({resource_id}, within)
        return calendars.get(resource_id)

    def load_all(self, resource_ids: set[ResourceId], within: TimeSlot) -> Calendars:
        calendars: dict[ResourceId, dict[Owner, list[TimeSlot]]] = defaultdict(
            lambda: defaultdict(list)
        )

        stmt = self._stmt(resource_ids, within)
        rows = self._session.execute(stmt).all()

        for row in rows:
            key = ResourceId(row.resource_id)
            owner = Owner(row.taken_by)
            loaded_slot = TimeSlot(row.start_date, row.end_date)
            calendars[key][owner].append(loaded_slot)

        return Calendars(
            {
                resource_id: Calendar(resource_id, calendar)
                for resource_id, calendar in calendars.items()
            }
        )

    def _stmt(
        self, resource_ids: set[ResourceId], within: TimeSlot
    ) -> Select[ReadModelRow]:
        availability_with_lag = (
            select(
                availabilities.c.resource_id,
                availabilities.c.taken_by,
                availabilities.c.from_date,
                availabilities.c.to_date,
                func.coalesce(
                    func.lag(availabilities.c.to_date).over(
                        partition_by=[
                            availabilities.c.resource_id,
                            availabilities.c.taken_by,
                        ],
                        order_by=availabilities.c.from_date,
                    ),
                    availabilities.c.from_date,
                ).label("prev_to_date"),
            )
            .filter(
                availabilities.c.resource_id.in_(
                    [resource_id.id for resource_id in resource_ids]
                ),
                availabilities.c.from_date >= within.from_,
                availabilities.c.to_date <= within.to,
            )
            .cte("availability_with_lag")
        )

        grouped_availability = select(
            availability_with_lag.c.resource_id,
            availability_with_lag.c.taken_by,
            availability_with_lag.c.from_date,
            availability_with_lag.c.to_date,
            availability_with_lag.c.prev_to_date,
            case(
                (
                    availability_with_lag.c.from_date
                    == availability_with_lag.c.prev_to_date,
                    0,
                ),
                else_=1,
            ).label("new_group_flag"),
            func.sum(
                case(
                    (
                        availability_with_lag.c.from_date
                        == availability_with_lag.c.prev_to_date,
                        0,
                    ),
                    else_=1,
                )
            )
            .over(
                partition_by=[
                    availability_with_lag.c.resource_id,
                    availability_with_lag.c.taken_by,
                ],
                order_by=availability_with_lag.c.from_date,
            )
            .label("grp"),
        ).cte("grouped_availability")

        stmt = (
            select(
                grouped_availability.c.resource_id,
                grouped_availability.c.taken_by,
                func.min(grouped_availability.c.from_date).label("start_date"),
                func.max(grouped_availability.c.to_date).label("end_date"),
            )
            .group_by(
                grouped_availability.c.resource_id,
                grouped_availability.c.taken_by,
                grouped_availability.c.grp,
            )
            .order_by("start_date")
        )

        return stmt


class ReadModelRow(tuple[UUID, UUID, datetime, datetime]):
    resource_id: UUID
    taken_by: UUID
    start_date: datetime
    end_date: datetime
