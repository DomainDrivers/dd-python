from smartschedule.allocation.capabilityscheduling.allocatable_capability import (
    AllocatableCapability,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_capability_repository import (
    AllocatableCapabilityRepository,
)
from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import (
    CapabilitySelector,
)
from smartschedule.shared.timeslot.time_slot import TimeSlot


class CapabilityScheduler:
    def __init__(
        self,
        availability_facade: AvailabilityFacade,
        allocatable_capability_repository: AllocatableCapabilityRepository,
    ) -> None:
        self._availability_facade = availability_facade
        self._repository = allocatable_capability_repository

    def schedule_resource_capabilities_for_period(
        self,
        resource_id: AllocatableResourceId,
        capabilities: list[CapabilitySelector],
        time_slot: TimeSlot,
    ) -> list[AllocatableCapabilityId]:
        allocatable_resource_ids = self._create_allocatable_resources(
            resource_id, capabilities, time_slot
        )
        for allocatable_resource_id in allocatable_resource_ids:
            availability_id = allocatable_resource_id.to_availability_resource_id()
            self._availability_facade.create_resource_slots(availability_id, time_slot)
        return allocatable_resource_ids

    def schedule_multiple_resources_for_period(
        self,
        resources: set[AllocatableResourceId],
        capability: Capability,
        time_slot: TimeSlot,
    ) -> list[AllocatableCapabilityId]:
        allocatable_capabilities = [
            AllocatableCapability(
                resource, CapabilitySelector.can_just_perform(capability), time_slot
            )
            for resource in resources
        ]
        self._repository.add_all(allocatable_capabilities)
        for allocatable_capability in allocatable_capabilities:
            resource_id = allocatable_capability.id.to_availability_resource_id()
            self._availability_facade.create_resource_slots(resource_id, time_slot)

        return [
            allocatable_capability.id
            for allocatable_capability in allocatable_capabilities
        ]

    def find_resource_capablities(
        self,
        allocatable_resource_id: AllocatableResourceId,
        capability: Capability,
        period: TimeSlot,
    ) -> AllocatableCapabilityId | None:
        allocatable_capability = (
            self._repository.find_by_resource_id_and_capability_and_time_slot(
                allocatable_resource_id,
                capability.name,
                capability.type,
                period.from_,
                period.to,
            )
        )
        return allocatable_capability.id if allocatable_capability else None

    def find_resource_performing_capabilities(
        self,
        allocatable_resource_id: AllocatableResourceId,
        capabilities: set[Capability],
        time_slot: TimeSlot,
    ) -> AllocatableCapabilityId | None:
        allocatable_capabilities = self._repository.find_by_resource_id_and_time_slot(
            allocatable_resource_id, time_slot.from_, time_slot.to
        )
        matching = [
            ac.id for ac in allocatable_capabilities if ac.can_perform(capabilities)
        ]
        return next(iter(matching), None)

    def _create_allocatable_resources(
        self,
        resource_id: AllocatableResourceId,
        capabilities: list[CapabilitySelector],
        time_slot: TimeSlot,
    ) -> list[AllocatableCapabilityId]:
        allocatable_capabilities = [
            AllocatableCapability(resource_id, capability, time_slot)
            for capability in capabilities
        ]
        self._repository.add_all(allocatable_capabilities)
        return [
            allocatable_capability.id
            for allocatable_capability in allocatable_capabilities
        ]
