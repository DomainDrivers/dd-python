from datetime import datetime, timedelta
from typing import Final
from uuid import uuid4

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.capabilities_allocated import CapabilitiesAllocated
from smartschedule.allocation.capability_released import CapabilityReleased
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations import ProjectAllocations
from smartschedule.allocation.project_allocations_demands_scheduled import (
    ProjectAllocationsDemandsScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestAllocationsToProject:
    WHEN: Final = datetime.min
    PROJECT_ID: Final = ProjectAllocationsId.new_one()
    ADMIN_ID: Final = ResourceId.new_one()
    FEB_1: Final = TimeSlot.create_daily_time_slot_at_utc(2020, 2, 1)
    FEB_2: Final = TimeSlot.create_daily_time_slot_at_utc(2020, 2, 2)
    JANUARY: Final = TimeSlot.create_daily_time_slot_at_utc(2020, 1, 1)
    FEBRUARY: Final = TimeSlot.create_daily_time_slot_at_utc(2020, 2, 1)

    def test_allocate(self) -> None:
        allocations = ProjectAllocations.empty(self.PROJECT_ID)

        event = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )

        assert isinstance(event, CapabilitiesAllocated)
        assert event == CapabilitiesAllocated(
            allocated_capability_id=event.allocated_capability_id,
            project_id=self.PROJECT_ID,
            missing_demands=Demands.none(),
            occurred_at=self.WHEN,
            event_id=event.event_id,
        )

    def test_cant_allocate_when_requested_slot_not_within_project_slot(self) -> None:
        allocations = ProjectAllocations(
            self.PROJECT_ID, Allocations.none(), Demands.none(), self.JANUARY
        )

        event = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )

        assert event is None

    def test_allocating_has_no_effect_when_capability_already_allocated(self) -> None:
        allocations = ProjectAllocations.empty(self.PROJECT_ID)
        allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )

        event = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )

        assert event is None

    def test_there_are_no_missing_demands_when_all_allocated(self) -> None:
        demands = Demands.of(
            Demand(Capability.permission("admin"), self.FEB_1),
            Demand(Capability.skill("java"), self.FEB_1),
        )
        allocations = ProjectAllocations.with_demands(self.PROJECT_ID, demands)
        allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )

        event = allocations.allocate(
            self.ADMIN_ID, Capability.skill("java"), self.FEB_1, self.WHEN
        )

        assert isinstance(event, CapabilitiesAllocated)
        assert event == CapabilitiesAllocated(
            allocated_capability_id=event.allocated_capability_id,
            project_id=self.PROJECT_ID,
            missing_demands=Demands.none(),
            occurred_at=self.WHEN,
            event_id=event.event_id,
        )

    def test_missing_demands_are_present_when_allocating_for_different_than_demanded_slot(
        self,
    ) -> None:
        demands = Demands.of(
            Demand(Capability.permission("admin"), self.FEB_1),
            Demand(Capability.skill("java"), self.FEB_1),
        )
        allocations = ProjectAllocations.with_demands(self.PROJECT_ID, demands)
        allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )

        event = allocations.allocate(
            self.ADMIN_ID, Capability.skill("java"), self.FEB_2, self.WHEN
        )

        assert isinstance(event, CapabilitiesAllocated)
        assert allocations.missing_demands() == Demands.of(
            Demand(Capability.skill("java"), self.FEB_1)
        )
        assert event == CapabilitiesAllocated(
            allocated_capability_id=event.allocated_capability_id,
            project_id=self.PROJECT_ID,
            missing_demands=Demands.of(Demand(Capability.skill("java"), self.FEB_1)),
            occurred_at=self.WHEN,
            event_id=event.event_id,
        )

    def test_release(self) -> None:
        allocations = ProjectAllocations.empty(self.PROJECT_ID)
        allocated_admin = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )
        assert allocated_admin is not None

        event = allocations.release(
            allocated_admin.allocated_capability_id, self.FEB_1, self.WHEN
        )

        assert isinstance(event, CapabilityReleased)
        assert event == CapabilityReleased(
            self.PROJECT_ID, Demands.none(), self.WHEN, event.event_id
        )

    def test_releasing_has_no_effect_when_capability_was_not_allocated(self) -> None:
        allocations = ProjectAllocations.empty(self.PROJECT_ID)

        event = allocations.release(uuid4(), self.FEB_1, self.WHEN)

        assert event is None

    def test_missing_demands_are_present_after_releasing_some_of_allocated_capabilities(
        self,
    ) -> None:
        demand_for_java = Demand(Capability.skill("java"), self.FEB_1)
        demand_for_admin = Demand(Capability.permission("admin"), self.FEB_1)
        allocations = ProjectAllocations.with_demands(
            self.PROJECT_ID, Demands.of(demand_for_admin, demand_for_java)
        )
        allocated_admin = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )
        assert allocated_admin is not None
        allocations.allocate(
            self.ADMIN_ID, Capability.skill("java"), self.FEB_1, self.WHEN
        )

        event = allocations.release(
            allocated_admin.allocated_capability_id, self.FEB_1, self.WHEN
        )

        assert isinstance(event, CapabilityReleased)
        assert event == CapabilityReleased(
            self.PROJECT_ID, Demands.of(demand_for_admin), self.WHEN, event.event_id
        )

    def test_releasing_has_no_effect_when_releasing_slot_not_within_allocated_slot(
        self,
    ) -> None:
        allocations = ProjectAllocations.empty(self.PROJECT_ID)
        allocated_admin = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )
        assert allocated_admin is not None

        event = allocations.release(
            allocated_admin.allocated_capability_id, self.FEB_2, self.WHEN
        )

        assert event is None

    def test_releasing_small_part_of_slot_leaves_the_rest(self) -> None:
        allocations = ProjectAllocations.empty(self.PROJECT_ID)
        allocated_admin = allocations.allocate(
            self.ADMIN_ID, Capability.permission("admin"), self.FEB_1, self.WHEN
        )
        assert allocated_admin is not None

        fifteen_minutes_in_1_feb = TimeSlot(
            self.FEB_1.from_ + timedelta(hours=1), self.FEB_1.from_ + timedelta(hours=2)
        )
        one_hour_before = TimeSlot(
            self.FEB_1.from_, self.FEB_1.from_ + timedelta(hours=1)
        )
        the_rest = TimeSlot(self.FEB_1.from_ + timedelta(hours=2), self.FEB_1.to)

        event = allocations.release(
            allocated_admin.allocated_capability_id, fifteen_minutes_in_1_feb, self.WHEN
        )

        assert isinstance(event, CapabilityReleased)
        assert event == CapabilityReleased(
            self.PROJECT_ID, Demands.none(), self.WHEN, event.event_id
        )
        assert allocations.allocations.all == {
            AllocatedCapability(
                self.ADMIN_ID.id, Capability.permission("admin"), one_hour_before
            ),
            AllocatedCapability(
                self.ADMIN_ID.id, Capability.permission("admin"), the_rest
            ),
        }

    def test_change_demands(self) -> None:
        admin_permission = Demand(Capability.permission("ADMIN"), self.FEB_1)
        java_skill = Demand(Capability.skill("JAVA"), self.FEB_1)
        demands = Demands.of(admin_permission, java_skill)
        allocations = ProjectAllocations.with_demands(self.PROJECT_ID, demands)

        allocations.allocate(
            self.ADMIN_ID, Capability.permission("ADMIN"), self.FEB_1, self.WHEN
        )

        python_skill = Demand(Capability.skill("PYTHON"), self.FEB_1)
        event = allocations.add_demands(Demands.of(python_skill), self.WHEN)

        assert allocations.missing_demands() == Demands.all_in_same_time_slot(
            self.FEB_1, Capability.skill("JAVA"), Capability.skill("PYTHON")
        )
        assert event == ProjectAllocationsDemandsScheduled(
            self.PROJECT_ID,
            Demands.all_in_same_time_slot(
                self.FEB_1, Capability.skill("JAVA"), Capability.skill("PYTHON")
            ),
            self.WHEN,
            event.uuid,
        )

    def test_change_project_dates(self) -> None:
        allocations = ProjectAllocations(
            self.PROJECT_ID, Allocations.none(), Demands.none(), self.JANUARY
        )

        event = allocations.define_slot(self.FEBRUARY, self.WHEN)

        assert event == ProjectAllocationScheduled(
            project_id=self.PROJECT_ID,
            from_to=self.FEBRUARY,
            occurred_at=self.WHEN,
            uuid=event.uuid,
        )
