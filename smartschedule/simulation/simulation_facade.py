from smartschedule.simulation.result import Result
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulated_project import SimulatedProject


class SimulationFacade:
    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self, projects: list[SimulatedProject], total_capability: SimulatedCapabilities
    ) -> Result:
        return Result(0.0, [], {})
