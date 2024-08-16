from __future__ import annotations

from decimal import Decimal

import factory  # type: ignore

from smartschedule.simulation.demands import Demands
from smartschedule.simulation.project_id import ProjectId
from smartschedule.simulation.simulated_project import SimulatedProject


class SimulatedProjectFactory(factory.Factory):  # type: ignore
    class Meta:
        model = SimulatedProject

    project_id = factory.LazyAttribute(lambda _: ProjectId.new_one())
    earnings = Decimal(0)
    missing_demands = factory.LazyAttribute(lambda _: Demands.of([]))
