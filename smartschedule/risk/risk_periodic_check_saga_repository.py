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

    def find_by_project_id_or_create(
        self, project_id: ProjectAllocationsId
    ) -> RiskPeriodicCheckSaga:
        try:
            return self.find_by_project_id(project_id)
        except self.NotFound:
            saga = RiskPeriodicCheckSaga(project_id)
            self.add(saga)
            return saga

    def find_by_project_id_in_or_else_create(
        self, interested: list[ProjectAllocationsId]
    ) -> Sequence[RiskPeriodicCheckSaga]:
        sagas = list(self.find_by_project_id_in(interested))
        found_ids = {found.project_id for found in sagas}
        missing_ids = set(interested) - found_ids
        for missing_id in missing_ids:
            saga = RiskPeriodicCheckSaga(missing_id)
            self.add(saga)
            sagas.append(saga)

        return sagas
