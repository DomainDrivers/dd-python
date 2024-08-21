from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.potential_transfers import PotentialTransfers
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulation_facade import SimulationFacade


class PotentialTransfersService:
    def __init__(self, simulation_facade: SimulationFacade) -> None:
        self._simulation_facade = simulation_facade

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
