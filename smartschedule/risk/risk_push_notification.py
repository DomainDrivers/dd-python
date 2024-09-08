from smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.demands import Demands
from smartschedule.planning.project_id import ProjectId
from smartschedule.shared.timeslot.time_slot import TimeSlot


class RiskPushNotification:
    def notify_demands_satisfied(self, project_id: ProjectAllocationsId) -> None:
        pass

    def notify_about_availability(
        self,
        project_id: ProjectAllocationsId,
        available: dict[Demand, AllocatableCapabilitiesSummary],
    ) -> None:
        pass

    def notify_profitable_relocation_found(
        self,
        project_id: ProjectAllocationsId,
        allocatable_capability_id: AllocatableCapabilityId,
    ) -> None:
        pass

    def notify_about_possible_risk(self, project_id: ProjectAllocationsId) -> None:
        pass

    def notify_about_possible_risk_during_planning(
        self, cause: ProjectId, demands: Demands
    ) -> None:
        pass

    def notify_about_critical_resource_not_available(
        self, cause: ProjectId, critical_resource: ResourceId, time_slot: TimeSlot
    ) -> None:
        pass

    def notify_about_resources_not_available(
        self, project_id: ProjectId, not_available: set[ResourceId]
    ) -> None:
        pass
