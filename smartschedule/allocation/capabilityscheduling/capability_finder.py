from smartschedule.allocation.capabilityscheduling.allocatable_capabilities_summary import (
    AllocatableCapabilitiesSummary,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability import (
    AllocatableCapability,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_summary import (
    AllocatableCapabilitySummary,
)
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class CapabilityFinder:
    def __init__(
        self,
        availability_facade: AvailabilityFacade,
        allocatable_capability_repository: AllocatableCapabilityRepository,
    ) -> None:
        self._availability_facade = availability_facade
        self._repository = allocatable_capability_repository

    def find_available_capabilities(
        self, capability: Capability, time_slot: TimeSlot
    ) -> AllocatableCapabilitiesSummary:
        found = self._repository.find_by_capability_within(
            capability.name, capability.type, time_slot.from_, time_slot.to
        )
        found = self._filter_availability_in_time_slot(found, time_slot)
        return self._create_summary(*found)

    def find_capabilities(
        self, capability: Capability, time_slot: TimeSlot
    ) -> AllocatableCapabilitiesSummary:
        found = self._repository.find_by_capability_within(
            capability.name, capability.type, time_slot.from_, time_slot.to
        )
        return self._create_summary(*found)

    def find_by_id(
        self, *allocatable_capability_ids: AllocatableCapabilityId
    ) -> AllocatableCapabilitiesSummary:
        found = self._repository.get_all(list(allocatable_capability_ids))
        return self._create_summary(*list(found))

    def _filter_availability_in_time_slot(
        self, allocatable_capabilities: list[AllocatableCapability], time_slot: TimeSlot
    ) -> list[AllocatableCapability]:
        availability_ids = {
            allocatable_capability.id.to_availability_resource_id()
            for allocatable_capability in allocatable_capabilities
        }
        calendars = self._availability_facade.load_calendars(
            availability_ids, time_slot
        )
        return [
            allocatable_capability
            for allocatable_capability in allocatable_capabilities
            if time_slot
            in calendars.get(
                allocatable_capability.id.to_availability_resource_id()
            ).available_slots()
        ]

    def _create_summary(
        self, *found: AllocatableCapability
    ) -> AllocatableCapabilitiesSummary:
        summaries = [
            AllocatableCapabilitySummary(
                allocatable_capability.id,
                allocatable_capability.resource_id,
                allocatable_capability.possible_capabilities,
                allocatable_capability.time_slot,
            )
            for allocatable_capability in found
        ]
        return AllocatableCapabilitiesSummary(all=summaries)
