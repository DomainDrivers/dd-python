from smartschedule.allocation.cashflow.cashflow import Cashflow
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.sqlalchemy_extensions import SQLAlchemyRepository


class CashflowRepository(SQLAlchemyRepository[Cashflow, ProjectAllocationsId]):
    pass
