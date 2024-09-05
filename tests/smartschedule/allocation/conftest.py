from typing import Callable, TypeAlias

import pytest
from lagom import Container

from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.allocation.capabilityscheduling.capability_scheduler import (
    CapabilityScheduler,
)
from smartschedule.availability.availability_facade import AvailabilityFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import CapabilitySelector
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.allocation.availability_assert import AvailabilityAssert


@pytest.fixture()
def allocation_facade(container: Container) -> AllocationFacade:
    return container.resolve(AllocationFacade)


AllocatableResourceFactory: TypeAlias = Callable[
    [TimeSlot, Capability, AllocatableResourceId], AllocatableCapabilityId
]


@pytest.fixture()
def allocatable_resource_factory(
    capability_scheduler: CapabilityScheduler,
) -> AllocatableResourceFactory:
    def _create_allocatable_resource(
        period: TimeSlot, capability: Capability, resource_id: AllocatableResourceId
    ) -> AllocatableCapabilityId:
        capabilities = [CapabilitySelector.can_just_perform(capability)]
        allocatable_capability_ids = (
            capability_scheduler.schedule_resource_capabilities_for_period(
                resource_id, capabilities, period
            )
        )
        assert len(allocatable_capability_ids) == 1
        return allocatable_capability_ids[0]

    return _create_allocatable_resource


@pytest.fixture()
def availability_assert(availability_facade: AvailabilityFacade) -> AvailabilityAssert:
    return AvailabilityAssert(availability_facade)


@pytest.fixture()
def capability_scheduler(container: Container) -> CapabilityScheduler:
    return container.resolve(CapabilityScheduler)
