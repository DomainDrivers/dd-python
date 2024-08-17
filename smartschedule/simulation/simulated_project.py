from dataclasses import dataclass
from decimal import Decimal

from smartschedule.simulation.demands import Demands
from smartschedule.simulation.project_id import ProjectId


@dataclass(frozen=True)
class SimulatedProject:
    project_id: ProjectId
    earnings: Decimal
    missing_demands: Demands

    def __hash__(self) -> int:
        return hash(self.project_id)
