from datetime import datetime

from sqlalchemy import DateTime, cast, select

from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class ProjectAllocationsRepository(
    SQLAlchemyRepository[ProjectAllocations, ProjectAllocationsId]
):
    def find_all_containing_date(self, when: datetime) -> list[ProjectAllocations]:
        stmt = select(self._type).filter(
            cast(self._type.time_slot["from_"].astext, DateTime) <= when,
            cast(self._type.time_slot["to"].astext, DateTime) > when,
        )
        return list(self._session.execute(stmt).scalars().all())
