from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from smartschedule.simulation.demands import Demands
from smartschedule.simulation.project_id import ProjectId


@dataclass(frozen=True)
class SimulatedProject:
    project_id: ProjectId
    value_getter: Callable[[], Decimal]
    missing_demands: Demands

    @property
    def value(self) -> Decimal:
        return self.value_getter()

    def __hash__(self) -> int:
        return hash(self.project_id)
