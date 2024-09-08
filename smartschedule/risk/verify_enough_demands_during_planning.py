from decimal import Decimal
from typing import Final
from uuid import uuid4

from smartschedule.planning.capabilities_demanded import CapabilitiesDemanded
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.planning.project_card import ProjectCard
from smartschedule.resource.resource_facade import ResourceFacade
from smartschedule.risk.risk_push_notification import RiskPushNotification
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import CapabilitySelector
from smartschedule.shared.event_bus import EventBus
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)
from smartschedule.simulation.demand import Demand
from smartschedule.simulation.demands import Demands
from smartschedule.simulation.project_id import ProjectId
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulated_project import SimulatedProject
from smartschedule.simulation.simulation_facade import SimulationFacade


@EventBus.has_event_handlers
class VerifyEnoughDemandsDuringPlanning:
    SAME_ARBITRARY_VALUE_FOR_EVERY_PROJECT: Final = Decimal(100)

    def __init__(
        self,
        planning_facade: PlanningFacade,
        simulation_facade: SimulationFacade,
        resource_facade: ResourceFacade,
        risk_push_notification: RiskPushNotification,
    ) -> None:
        self._planning_facade = planning_facade
        self._simulation_facade = simulation_facade
        self._resource_facade = resource_facade
        self._risk_push_notification = risk_push_notification

    @EventBus.async_event_handler
    def handle(self, event: CapabilitiesDemanded) -> None:
        project_summaries = self._planning_facade.load_all()
        all_capabilities = self._resource_facade.find_all_capabilities()
        result = self._not_able_to_handle_all_projects_given_capabilities(
            project_summaries, all_capabilities
        )
        if result:
            self._risk_push_notification.notify_about_possible_risk_during_planning(
                event.project_id, event.demands
            )

    def _not_able_to_handle_all_projects_given_capabilities(
        self, project_summaries: list[ProjectCard], all_capabilities: list[Capability]
    ) -> bool:
        capabilities = [
            AvailableResourceCapability(
                uuid4(),
                CapabilitySelector.can_just_perform(capability),
                TimeSlot.empty(),
            )
            for capability in all_capabilities
        ]
        simulated_projects = [
            self._same_priced_simulated_project(summary)
            for summary in project_summaries
        ]
        result = self._simulation_facade.what_is_the_optimal_setup(
            simulated_projects, SimulatedCapabilities(capabilities)
        )
        return len(result.chosen_items) != len(project_summaries)

    def _same_priced_simulated_project(self, card: ProjectCard) -> SimulatedProject:
        simulated_demands = [
            Demand(demand.capability, TimeSlot.empty()) for demand in card.demands.all
        ]
        return SimulatedProject(
            ProjectId(card.project_id.id),
            lambda: self.SAME_ARBITRARY_VALUE_FOR_EVERY_PROJECT,
            Demands(simulated_demands),
        )
