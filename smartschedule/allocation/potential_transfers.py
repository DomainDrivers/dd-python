from __future__ import annotations

import functools
from dataclasses import dataclass

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.projects_allocations_summary import (
    ProjectsAllocationsSummary,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.demand import Demand
from smartschedule.simulation.demands import Demands
from smartschedule.simulation.project_id import ProjectId
from smartschedule.simulation.simulated_project import SimulatedProject


@dataclass(frozen=True)
class PotentialTransfers:
    summary: ProjectsAllocationsSummary
    earnings: dict[ProjectAllocationsId, Earnings]

    def transfer(
        self,
        project_from: ProjectAllocationsId,
        project_to: ProjectAllocationsId,
        allocated_capability: AllocatedCapability,
        for_slot: TimeSlot,
    ) -> PotentialTransfers:
        try:
            allocations_from = self.summary.project_allocations[project_from]
            allocations_to = self.summary.project_allocations[project_to]
        except KeyError:
            return self

        new_allocations_project_from = allocations_from.remove(
            allocated_capability.allocated_capability_id, for_slot
        )
        if new_allocations_project_from == allocations_from:
            return self
        self.summary.project_allocations[project_from] = new_allocations_project_from
        new_allocations_project_to = allocations_to.add(
            AllocatedCapability(
                allocated_capability.allocated_capability_id,
                allocated_capability.capability,
                for_slot,
            )
        )
        self.summary.project_allocations[project_to] = new_allocations_project_to
        return PotentialTransfers(self.summary, self.earnings)

    def to_simulated_projects(self) -> list[SimulatedProject]:
        return [
            SimulatedProject(
                project_id=ProjectId(project_id.id),
                value_getter=functools.partial(
                    lambda value: value, self.earnings[project_id].to_decimal()
                ),
                missing_demands=self._missing_demands(project_id),
            )
            for project_id in self.summary.project_allocations.keys()
        ]

    def _missing_demands(self, project_id: ProjectAllocationsId) -> Demands:
        allocations = self.summary.project_allocations[project_id]
        all_demands = self.summary.demands[project_id].missing_demands(allocations)
        return Demands.of(
            [
                Demand(capability=demand.capability, slot=demand.time_slot)
                for demand in all_demands.all
            ]
        )
