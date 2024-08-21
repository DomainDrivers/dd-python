from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocations import Allocations
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.potential_transfers import PotentialTransfers
from smartschedule.allocation.potential_transfers_service import (
    PotentialTransfersService,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.allocation.projects_allocations_summary import (
    ProjectsAllocationsSummary,
)
from smartschedule.optimization.optimization_facade import OptimizationFacade
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot
from smartschedule.simulation.simulation_facade import SimulationFacade


@pytest.fixture()
def jan_1() -> TimeSlot:
    return TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)


@pytest.fixture()
def fifteen_minutes_in_jan(jan_1: TimeSlot) -> TimeSlot:
    return TimeSlot(jan_1.from_, jan_1.from_ + timedelta(minutes=15))


@pytest.fixture()
def demand_for_java_just_for_15min_in_jan(fifteen_minutes_in_jan: TimeSlot) -> Demands:
    return Demands([Demand(Capability.skill("JAVA-MID"), fifteen_minutes_in_jan)])


@pytest.fixture()
def demand_for_java_mid_in_jan(jan_1: TimeSlot) -> Demands:
    return Demands([Demand(Capability.skill("JAVA-MID"), jan_1)])


@pytest.fixture()
def demands_for_java_and_python_in_jan(jan_1: TimeSlot) -> Demands:
    return Demands(
        [
            Demand(Capability.skill("JAVA-MID"), jan_1),
            Demand(Capability.skill("PYTHON-MID"), jan_1),
        ]
    )


@pytest.fixture()
def banking_soft_id() -> ProjectAllocationsId:
    return ProjectAllocationsId.new_one()


@pytest.fixture()
def insurance_soft_id() -> ProjectAllocationsId:
    return ProjectAllocationsId.new_one()


@pytest.fixture()
def staszek_java_mid(jan_1: TimeSlot) -> AllocatedCapability:
    return AllocatedCapability(uuid4(), Capability.skill("JAVA-MID"), jan_1)


@pytest.fixture()
def potential_transfers_service() -> PotentialTransfersService:
    return PotentialTransfersService(SimulationFacade(OptimizationFacade()))


class TestPotentialTransferScenarios:
    def test_simulates_moving_capabilities_to_different_project(
        self,
        demand_for_java_mid_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        jan_1: TimeSlot,
        potential_transfers_service: PotentialTransfersService,
    ) -> None:
        banking_soft = Project(banking_soft_id, demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(
            insurance_soft_id, demand_for_java_mid_in_jan, Decimal(90)
        )
        banking_soft.add(staszek_java_mid)
        potential_transfers = self._to_potential_transfers(banking_soft, insurance_soft)

        result = potential_transfers_service.check_potential_transfer(
            potential_transfers,
            banking_soft_id,
            insurance_soft_id,
            staszek_java_mid,
            jan_1,
        )

        assert result == 81

    def test_simulates_moving_capabilities_to_different_project_just_for_a_while(
        self,
        demand_for_java_mid_in_jan: Demands,
        demand_for_java_just_for_15min_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        fifteen_minutes_in_jan: TimeSlot,
        potential_transfers_service: PotentialTransfersService,
    ) -> None:
        banking_soft = Project(banking_soft_id, demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(
            insurance_soft_id, demand_for_java_just_for_15min_in_jan, Decimal(99)
        )
        banking_soft.add(staszek_java_mid)
        potential_transfers = self._to_potential_transfers(banking_soft, insurance_soft)

        result = potential_transfers_service.check_potential_transfer(
            potential_transfers,
            banking_soft_id,
            insurance_soft_id,
            staszek_java_mid,
            fifteen_minutes_in_jan,
        )

        assert result == 90

    def test_the_move_gives_zero_profit_when_there_are_still_missing_demands(
        self,
        demand_for_java_mid_in_jan: Demands,
        demands_for_java_and_python_in_jan: Demands,
        banking_soft_id: ProjectAllocationsId,
        insurance_soft_id: ProjectAllocationsId,
        staszek_java_mid: AllocatedCapability,
        jan_1: TimeSlot,
        potential_transfers_service: PotentialTransfersService,
    ) -> None:
        banking_soft = Project(banking_soft_id, demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(
            insurance_soft_id, demands_for_java_and_python_in_jan, Decimal(99)
        )
        banking_soft.add(staszek_java_mid)
        potential_transfers = self._to_potential_transfers(banking_soft, insurance_soft)

        result = potential_transfers_service.check_potential_transfer(
            potential_transfers,
            banking_soft_id,
            insurance_soft_id,
            staszek_java_mid,
            jan_1,
        )

        assert result == -9

    @staticmethod
    def _to_potential_transfers(*projects: Project) -> PotentialTransfers:
        allocations: dict[ProjectAllocationsId, Allocations] = {}
        demands: dict[ProjectAllocationsId, Demands] = {}
        earnings: dict[ProjectAllocationsId, Decimal] = {}
        for project in projects:
            allocations[project.id] = project.allocations
            demands[project.id] = project.demands
            earnings[project.id] = project.earnings
        return PotentialTransfers(
            ProjectsAllocationsSummary({}, allocations, demands), earnings
        )


class Project:
    def __init__(
        self, id: ProjectAllocationsId, demands: Demands, earnings: Decimal
    ) -> None:
        self.id = id
        self.earnings = earnings
        self.demands = demands
        self.allocations = Allocations.none()

    def add(self, allocated_capability: AllocatedCapability) -> Project:
        self.allocations = self.allocations.add(allocated_capability)
        return self
