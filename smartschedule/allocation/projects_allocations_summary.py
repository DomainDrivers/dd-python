from __future__ import annotations

from dataclasses import dataclass

from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class ProjectsAllocationsSummary:
    time_slots: dict[ProjectAllocationsId, TimeSlot]
    project_allocations: dict[ProjectAllocationsId, Allocations]
    demands: dict[ProjectAllocationsId, Demands]

    @staticmethod
    def of(*all_project_allocations: ProjectAllocations) -> ProjectsAllocationsSummary:
        time_slots = {
            project_allocations.project_id: project_allocations.time_slot
            for project_allocations in all_project_allocations
            if project_allocations.has_time_slot()
        }
        allocations = {
            project_allocations.project_id: project_allocations.allocations
            for project_allocations in all_project_allocations
        }
        demands = {
            project_allocations.project_id: project_allocations.demands
            for project_allocations in all_project_allocations
        }
        return ProjectsAllocationsSummary(time_slots, allocations, demands)
