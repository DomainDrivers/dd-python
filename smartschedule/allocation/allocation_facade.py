from uuid import UUID

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.projects import Projects
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulation_facade import SimulationFacade


class AllocationFacade:
    def __init__(self, simulation_facade: SimulationFacade) -> None:
        self._simulation_facade = simulation_facade

    def check_potential_transfer(
        self,
        projects: Projects,
        project_from: UUID,
        project_to: UUID,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> float:
        # Project rather fetched from a DB.
        result_before = self._simulation_facade.what_is_the_optimal_setup(
            projects.to_simulated_projects(), SimulatedCapabilities.none()
        )

        projects = projects.transfer(project_from, project_to, capability, for_slot)
        result_after = self._simulation_facade.what_is_the_optimal_setup(
            projects.to_simulated_projects(), SimulatedCapabilities.none()
        )

        return result_after.profit - result_before.profit
