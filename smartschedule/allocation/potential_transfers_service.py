from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)
from smartschedule.allocation.cashflow.cash_flow_facade import CashFlowFacade
from smartschedule.allocation.potential_transfers import PotentialTransfers
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.project_allocations_repository import (
    ProjectAllocationsRepository,
)
from smartschedule.allocation.projects_allocations_summary import (
    ProjectsAllocationsSummary,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulation_facade import SimulationFacade


class PotentialTransfersService:
    def __init__(
        self,
        simulation_facade: SimulationFacade,
        cashflow_facade: CashFlowFacade,
        project_allocations_repository: ProjectAllocationsRepository,
    ) -> None:
        self._simulation_facade = simulation_facade
        self._cashflow_facade = cashflow_facade
        self._project_allocations_repository = project_allocations_repository

    def profit_after_moving_capabilities(
        self,
        project_id: ProjectAllocationsId,
        capability_to_move: AllocatableCapabilitySummary,
        time_slot: TimeSlot,
    ) -> float:
        # cached?
        potential_transfers = PotentialTransfers(
            ProjectsAllocationsSummary.of(
                *self._project_allocations_repository.get_all()
            ),
            self._cashflow_facade.find_all(),
        )
        return self._check_potential_transfer(
            potential_transfers, project_id, capability_to_move, time_slot
        )

    def _check_potential_transfer(
        self,
        transfers: PotentialTransfers,
        project_to: ProjectAllocationsId,
        capability_to_move: AllocatableCapabilitySummary,
        time_slot: TimeSlot,
    ) -> float:
        result_before = self._simulation_facade.what_is_the_optimal_setup(
            transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        after_transfer = transfers.transfer_capabilities(
            project_to=project_to,
            capability_to_transfer=capability_to_move,
            for_slot=time_slot,
        )
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            after_transfer.to_simulated_projects(), SimulatedCapabilities.none()
        )
        return result_after.profit - result_before.profit

    def check_potential_transfer(
        self,
        transfers: PotentialTransfers,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> float:
        result_before = self._simulation_facade.what_is_the_optimal_setup(
            transfers.to_simulated_projects(), SimulatedCapabilities.none()
        )
        after_transfer = transfers.transfer(
            project_from, project_to, capability, for_slot
        )
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            after_transfer.to_simulated_projects(), SimulatedCapabilities.none()
        )
        return result_after.profit - result_before.profit
