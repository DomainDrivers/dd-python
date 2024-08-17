from __future__ import annotations

import functools
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.project import Project
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.demand import Demand as SimulationDemand
from smartschedule.simulation.demands import Demands as SimulationDemands
from smartschedule.simulation.project_id import ProjectId
from smartschedule.simulation.simulated_project import SimulatedProject


@dataclass(frozen=True)
class Projects:
    projects: dict[UUID, Project]

    def transfer(
        self,
        project_from: UUID,
        project_to: UUID,
        capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> Projects:
        try:
            from_ = self.projects[project_from]
            to = self.projects[project_to]
        except KeyError:
            return self

        removed = from_.remove(capability, for_slot)
        if removed is None:
            return self

        to.add(AllocatedCapability(removed.resource_id, removed.capability, for_slot))
        return self

    def to_simulated_projects(self) -> list[SimulatedProject]:
        result = []
        for project_id, project in self.projects.items():

            def value_getter(earnings: Decimal) -> Decimal:
                return earnings

            result.append(
                SimulatedProject(
                    ProjectId(project_id),
                    functools.partial(value_getter, project.earnings),
                    self._get_missing_demands(project),
                )
            )

        return result

    def _get_missing_demands(self, project: Project) -> SimulationDemands:
        all_demands = project.missing_demands.all
        return SimulationDemands(
            [
                SimulationDemand(demand.capability, demand.time_slot)
                for demand in all_demands
            ]
        )
