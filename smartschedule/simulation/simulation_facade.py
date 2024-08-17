from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.optimization.item import Item
from smartschedule.optimization.optimization_facade import OptimizationFacade
from smartschedule.optimization.result import Result
from smartschedule.optimization.total_capacity import TotalCapacity
from smartschedule.optimization.total_weight import TotalWeight
from smartschedule.optimization.weight_dimension import WeightDimension
from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulated_project import SimulatedProject


class SimulationFacade:
    def __init__(self, optimization_facade: OptimizationFacade) -> None:
        self._optimization_facade = optimization_facade

    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self,
        projects_simulations: list[SimulatedProject],
        total_capability: SimulatedCapabilities,
    ) -> Result[AvailableResourceCapability]:
        return self._optimization_facade.calculate(
            self._to_items(projects_simulations), self._to_capacity(total_capability)
        )

    def _to_capacity(
        self, simulated_capabilities: SimulatedCapabilities
    ) -> TotalCapacity:
        capabilities = simulated_capabilities.capabilities
        capacity_dimensions: list[CapacityDimension] = list(
            capabilities
        )  # list is invariant, need this explicitly
        return TotalCapacity(capacity_dimensions)

    def _to_items(
        self, projects_simulations: list[SimulatedProject]
    ) -> list[Item[AvailableResourceCapability]]:
        return [self._to_item(project) for project in projects_simulations]

    def _to_item(
        self, simulated_project: SimulatedProject
    ) -> Item[AvailableResourceCapability]:
        missing_demands = simulated_project.missing_demands.all
        weights: list[WeightDimension[AvailableResourceCapability]] = list(
            missing_demands
        )
        return Item(
            str(simulated_project.project_id),
            float(simulated_project.earnings),
            TotalWeight(weights),
        )
