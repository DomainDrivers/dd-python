from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.allocation.cashflow.cost import Cost
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.income import Income
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.sqlalchemy_extensions import AsJSON, EmbeddedUUID, registry


@registry.mapped_as_dataclass()
class Cashflow:
    __tablename__ = "cashflows"

    project_id: Mapped[ProjectAllocationsId] = mapped_column(
        EmbeddedUUID[ProjectAllocationsId], primary_key=True
    )
    income: Mapped[Income] = mapped_column(AsJSON[Income])
    cost: Mapped[Cost] = mapped_column(AsJSON[Cost])

    def __init__(
        self, project_id: ProjectAllocationsId, income: Income, cost: Cost
    ) -> None:
        self.project_id = project_id
        self.income = income
        self.cost = cost

    @property
    def earnings(self) -> Earnings:
        return self.income - self.cost
