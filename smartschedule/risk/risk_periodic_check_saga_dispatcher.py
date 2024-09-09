import itertools
from datetime import datetime

from smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from smartschedule.allocation.capabilityscheduling.capability_finder import (
    CapabilityFinder,
)
from smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.not_satisfied_demands import NotSatisfiedDemands
from smartschedule.allocation.potential_transfers_service import (
    PotentialTransfersService,
)
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.resource_taken_over import ResourceTakenOver
from smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from smartschedule.risk.risk_periodic_check_saga_repository import (
    RiskPeriodicCheckSagaRepository,
)
from smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from smartschedule.risk.risk_push_notification import RiskPushNotification
from smartschedule.shared.event_bus import EventBus


@EventBus.has_event_handlers
class RiskPeriodicCheckSagaDispatcher:
    def __init__(
        self,
        state_repository: RiskPeriodicCheckSagaRepository,
        potential_transfers_service: PotentialTransfersService,
        capability_finder: CapabilityFinder,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._state_repository = state_repository
        self._potential_transfers_service = potential_transfers_service
        self._capability_finder = capability_finder
        self._risk_push_notification = risk_push_notification

    # remember about transactions spanning saga and potential external system
    @EventBus.async_event_handler
    def handle_project_allocations_scheduled(
        self, event: ProjectAllocationScheduled
    ) -> None:
        saga = self._state_repository.find_by_project_id(event.project_id)
        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    @EventBus.async_event_handler
    def handle_not_satisfied_demands(self, event: NotSatisfiedDemands) -> None:
        project_ids = list(event.missing_demands.keys())
        sagas = self._state_repository.find_by_project_id_in_or_else_create(project_ids)
        next_steps: list[tuple[RiskPeriodicCheckSaga, RiskPeriodicCheckSagaStep]] = []
        for saga in sagas:
            missing_demands = event.missing_demands[saga.project_id]
            next_step = saga.set_missing_demands(missing_demands)
            next_steps.append((saga, next_step))
        self._state_repository.add_all(sagas)
        for saga, next_step in next_steps:
            self._perform(next_step, saga)

    # remember about transactions spanning saga and potential external system
    @EventBus.async_event_handler
    def handle_earnings_recalculated(self, event: EarningsRecalculated) -> None:
        try:
            saga = self._state_repository.find_by_project_id(event.project_id)
        except self._state_repository.NotFound:
            saga = RiskPeriodicCheckSaga(event.project_id, earnings=event.earnings)

        next_step = saga.handle(event)
        self._state_repository.add(saga)
        self._perform(next_step, saga)

    @EventBus.async_event_handler
    def handle_resource_taken_over(self, event: ResourceTakenOver) -> None:
        interested = [ProjectAllocationsId(owner.id) for owner in event.previous_owners]
        # transaction per one saga
        sagas = self._state_repository.find_by_project_id_in(interested)
        for saga in sagas:
            next_step = saga.handle(event)
            self._state_repository.add(saga)
            self._perform(next_step, saga)

    # To be called periodically in some sort of cron job, e.g. Celery Beat
    def handle_weekly_check(self) -> None:
        sagas = self._state_repository.get_all()
        now = datetime.now()
        for saga in sagas:
            next_step = saga.handle_weekly_check(now)
            self._state_repository.add(saga)
            self._perform(next_step, saga)

    def _perform(
        self, next_step: RiskPeriodicCheckSagaStep, saga: RiskPeriodicCheckSaga
    ) -> None:
        if next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED:
            self._risk_push_notification.notify_demands_satisfied(saga.project_id)
        elif next_step == RiskPeriodicCheckSagaStep.FIND_AVAILABLE:
            self._handle_find_available_for(saga)
        elif next_step == RiskPeriodicCheckSagaStep.DO_NOTHING:
            return
        elif next_step == RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT:
            self._handle_simulate_relocation(saga)
        elif next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK:
            self._risk_push_notification.notify_about_possible_risk(saga.project_id)

    def _handle_find_available_for(self, saga: RiskPeriodicCheckSaga) -> None:
        replacements = self._find_available_replacements_for(saga.missing_demands)
        allocatable_capabilities = list(
            itertools.chain(*[summary.all for summary in replacements.values()])
        )
        if not len(allocatable_capabilities) == 0:
            self._risk_push_notification.notify_about_availability(
                saga.project_id, replacements
            )

    def _handle_simulate_relocation(self, saga: RiskPeriodicCheckSaga) -> None:
        all_replacements = self._find_possible_replacements_for(saga.missing_demands)
        for _demand, replacements in all_replacements.items():
            for replacement in replacements.all:
                profit_after_moving_capabilities = (
                    self._potential_transfers_service.profit_after_moving_capabilities(
                        saga.project_id, replacement, replacement.time_slot
                    )
                )
                if profit_after_moving_capabilities > 0:
                    self._risk_push_notification.notify_profitable_relocation_found(
                        saga.project_id, replacement.id
                    )

    def _find_available_replacements_for(
        self, demands: Demands
    ) -> dict[Demand, AllocatableCapabilitiesSummary]:
        return {
            demand: self._capability_finder.find_available_capabilities(
                demand.capability, demand.time_slot
            )
            for demand in demands.all
        }

    def _find_possible_replacements_for(
        self, demands: Demands
    ) -> dict[Demand, AllocatableCapabilitiesSummary]:
        return {
            demand: self._capability_finder.find_capabilities(
                demand.capability, demand.time_slot
            )
            for demand in demands.all
        }
