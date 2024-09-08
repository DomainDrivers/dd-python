from __future__ import annotations

from datetime import datetime
from functools import singledispatchmethod
from typing import Any, Final

from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from smartschedule.allocation.capability_released import CapabilityReleased
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.resource_taken_over import ResourceTakenOver
from smartschedule.risk.risk_periodic_check_saga_id import RiskPeriodicCheckSagaId
from smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from smartschedule.shared.sqlalchemy_extensions import AsJSON, EmbeddedUUID, registry


@registry.mapped_as_dataclass(init=False)
class RiskPeriodicCheckSaga:
    RISK_THRESHOLD_VALUE: Final = Earnings(1000)
    UPCOMING_DEADLINE_AVAILABILITY_SEARCH: Final = 30
    UPCOMING_DEADLINE_REPLACEMENT_SUGGESTION: Final = 15

    __tablename__ = "project_risk_sagas"

    id: Mapped[RiskPeriodicCheckSagaId] = mapped_column(
        EmbeddedUUID[RiskPeriodicCheckSagaId], primary_key=True
    )
    project_id: Mapped[ProjectAllocationsId] = mapped_column(
        EmbeddedUUID[ProjectAllocationsId]
    )
    missing_demands: Mapped[Demands] = mapped_column(AsJSON[Demands])
    earnings: Mapped[Earnings] = mapped_column(AsJSON[Earnings])
    deadline: Mapped[datetime | None] = mapped_column(nullable=True)

    _version: Mapped[int] = mapped_column(name="version")
    __mapper_args__ = {"version_id_col": _version}

    def __init__(
        self,
        project_id: ProjectAllocationsId,
        missing_demands: Demands | None = None,
        earnings: Earnings | None = None,
    ) -> None:
        self.id = RiskPeriodicCheckSagaId.new_one()
        self.project_id = project_id
        self.missing_demands = missing_demands or Demands.none()
        self.earnings = earnings or Earnings(0)
        self.deadline = None

    def are_demands_satisfied(self) -> bool:
        return False

    @singledispatchmethod
    def handle(self, event: Any) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError(f"Unsupported event type - {type(event)}")

    @handle.register
    def _handle_earnings_recalculated(
        self, event: EarningsRecalculated
    ) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError

    @handle.register
    def _handle_project_allocations_demands_scheduled(
        self, event: ProjectAllocationsDemandsScheduled
    ) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError

    @handle.register
    def _handle_project_allocations_scheduled(
        self, event: ProjectAllocationScheduled
    ) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError

    @handle.register
    def _handle_resource_taken_over(
        self, event: ResourceTakenOver
    ) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError

    @handle.register
    def _handle_capability_released(
        self, event: CapabilityReleased
    ) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError

    @handle.register
    def _handle_capabilities_allocated(
        self, event: CapabilitiesAllocated
    ) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError

    def handle_weekly_check(self, when: datetime) -> RiskPeriodicCheckSagaStep:
        raise NotImplementedError
