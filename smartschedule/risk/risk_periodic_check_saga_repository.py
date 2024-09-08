from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class RiskPeriodicCheckSagaRepository(
    SQLAlchemyRepository[RiskPeriodicCheckSaga, RiskPeriodicCheckSagaId]
):
    def find_by_project_id(
        self, project_id: ProjectAllocationsId
    ) -> RiskPeriodicCheckSaga:
        stmt = select(self._type).filter(self._type.project_id == project_id)
        try:
            return self._session.execute(stmt).scalar_one()
        except NoResultFound:
            raise self.NotFound

    def find_by_project_id_in(
        self, interested: list[ProjectAllocationsId]
    ) -> Sequence[RiskPeriodicCheckSaga]:
        stmt = select(self._type).filter(self._type.project_id.in_(interested))
        return self._session.execute(stmt).scalars().all()
