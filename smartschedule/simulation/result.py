from dataclasses import dataclass

from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)
from smartschedule.simulation.simulated_project import SimulatedProject


@dataclass(frozen=True)
class Result:
    profit: float
    chosen_projects: list[SimulatedProject]
    resources_allocated_to_projects: dict[
        SimulatedProject, set[AvailableResourceCapability]
    ]

    def __str__(self) -> str:
        return f"Result{{profit={self.profit}, items={self.chosen_projects}}}"
