from smartschedule.allocation.cashflow.cashflow import Cashflow
from smartschedule.allocation.cashflow.cashflow_repository import CashflowRepository
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class SqlAlchemyCashflowRepository(
    SQLAlchemyRepository[Cashflow, ProjectAllocationsId], CashflowRepository
):
    pass
