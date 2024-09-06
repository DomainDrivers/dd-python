from __future__ import annotations

from smartschedule.allocation.capabilityscheduling.allocatable_resource_id import (
    AllocatableResourceId,
)
from smartschedule.allocation.capabilityscheduling.capability_scheduler import (
    CapabilityScheduler,
)
from smartschedule.allocation.capabilityscheduling.legacyacl import (
    translate_to_capability_selector,
)
from smartschedule.allocation.capabilityscheduling.legacyacl.employee_data_from_legacy_esb_message import (
    EmployeeDataFromLegacyEsbMessage,
)


class EmployeeCreatedInLegacySystemMessageHandler:
    def __init__(self, capability_scheduler: CapabilityScheduler) -> None:
        self._capability_scheduler = capability_scheduler

    # subscribe to message bus
    def handle(self, message: EmployeeDataFromLegacyEsbMessage) -> None:
        allocatable_resource_id = AllocatableResourceId(message.resource_id)
        capability_selectors = translate_to_capability_selector.translate(message)
        self._capability_scheduler.schedule_resource_capabilities_for_period(
            allocatable_resource_id, capability_selectors, message.time_slot
        )
