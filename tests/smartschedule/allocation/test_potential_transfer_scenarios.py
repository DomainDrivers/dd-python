from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from smartschedule.allocation.allocated_capability import AllocatedCapability
from smartschedule.allocation.allocation_facade import AllocationFacade
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project import Project
from smartschedule.allocation.projects import Projects
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
def banking_soft_id() -> UUID:
    return uuid4()


@pytest.fixture()
def insurance_soft_id() -> UUID:
    return uuid4()


@pytest.fixture()
def staszek_java_mid(jan_1: TimeSlot) -> AllocatedCapability:
    return AllocatedCapability(uuid4(), Capability.skill("JAVA-MID"), jan_1)


@pytest.fixture()
def allocation_facade() -> AllocationFacade:
    return AllocationFacade(SimulationFacade(OptimizationFacade()))


class TestPotentialTransferScenarios:
    def test_simulates_moving_capabilities_to_different_project(
        self,
        demand_for_java_mid_in_jan: Demands,
        banking_soft_id: UUID,
        insurance_soft_id: UUID,
        staszek_java_mid: AllocatedCapability,
        jan_1: TimeSlot,
        allocation_facade: AllocationFacade,
    ) -> None:
        banking_soft = Project(demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(demand_for_java_mid_in_jan, Decimal(90))
        projects = Projects(
            {banking_soft_id: banking_soft, insurance_soft_id: insurance_soft}
        )
        banking_soft.add(staszek_java_mid)

        result = allocation_facade.check_potential_transfer(
            projects, banking_soft_id, insurance_soft_id, staszek_java_mid, jan_1
        )

        assert result == 81

    def test_simulates_moving_capabilities_to_different_project_just_for_a_while(
        self,
        demand_for_java_mid_in_jan: Demands,
        demand_for_java_just_for_15min_in_jan: Demands,
        banking_soft_id: UUID,
        insurance_soft_id: UUID,
        staszek_java_mid: AllocatedCapability,
        fifteen_minutes_in_jan: TimeSlot,
        allocation_facade: AllocationFacade,
    ) -> None:
        banking_soft = Project(demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(demand_for_java_just_for_15min_in_jan, Decimal(99))
        projects = Projects(
            {banking_soft_id: banking_soft, insurance_soft_id: insurance_soft}
        )
        banking_soft.add(staszek_java_mid)

        result = allocation_facade.check_potential_transfer(
            projects,
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
        banking_soft_id: UUID,
        insurance_soft_id: UUID,
        staszek_java_mid: AllocatedCapability,
        jan_1: TimeSlot,
        allocation_facade: AllocationFacade,
    ) -> None:
        banking_soft = Project(demand_for_java_mid_in_jan, Decimal(9))
        insurance_soft = Project(demands_for_java_and_python_in_jan, Decimal(99))
        projects = Projects(
            {banking_soft_id: banking_soft, insurance_soft_id: insurance_soft}
        )
        banking_soft.add(staszek_java_mid)

        result = allocation_facade.check_potential_transfer(
            projects, banking_soft_id, insurance_soft_id, staszek_java_mid, jan_1
        )

        assert result == -9


# +package domaindrivers.smartschedule.allocation;
# +
# +import domaindrivers.smartschedule.optimization.OptimizationFacade;
# +import domaindrivers.smartschedule.shared.timeslot.TimeSlot;
# +import domaindrivers.smartschedule.simulation.*;
# +import org.junit.jupiter.api.Test;
# +
# +import java.time.temporal.ChronoUnit;
# +import java.util.List;
# +import java.util.Map;
# +import java.util.UUID;
# +
# +import static domaindrivers.smartschedule.shared.capability.Capability.skill;
# +import static java.math.BigDecimal.valueOf;
# +import static org.junit.jupiter.api.Assertions.assertEquals;
# +
# +class PotentialTransferScenarios {
# +
# +    static final TimeSlot JAN_1 = TimeSlot.createDailyTimeSlotAtUTC(2021, 1, 1);
# +    static final TimeSlot FIFTEEN_MINUTES_IN_JAN = new TimeSlot(JAN_1.from(), JAN_1.from().plus(15, ChronoUnit.MINUTES));
# +    static final Demands DEMAND_FOR_JAVA_JUST_FOR_15MIN_IN_JAN = new Demands(List.of(new Demand(skill("JAVA-MID"), FIFTEEN_MINUTES_IN_JAN)));
# +    static final Demands DEMAND_FOR_JAVA_MID_IN_JAN = new Demands(List.of(new Demand(skill("JAVA-MID"), JAN_1)));
# +    static final Demands DEMANDS_FOR_JAVA_AND_PYTHON_IN_JAN = new Demands(List.of(new Demand(skill("JAVA-MID"), JAN_1), new Demand(skill("PYTHON-MID"), JAN_1)));
# +
# +    static final UUID BANKING_SOFT_ID = UUID.randomUUID();
# +    static final UUID INSURANCE_SOFT_ID = UUID.randomUUID();
# +    static final AllocatedCapability STASZEK_JAVA_MID = new AllocatedCapability(UUID.randomUUID(), skill("JAVA-MID"), JAN_1);
# +
# +    AllocationFacade simulationFacade = new AllocationFacade(new SimulationFacade(new OptimizationFacade()));
# +
# +    @Test
# +    void simulatesMovingCapabilitiesToDifferentProject() {
# +        //given
# +        Project bankingSoft =
# +                new Project(DEMAND_FOR_JAVA_MID_IN_JAN, valueOf(9));
# +        Project insuranceSoft =
# +                new Project(DEMAND_FOR_JAVA_MID_IN_JAN, valueOf(90));
# +        Projects projects = new Projects(
# +                Map.of(BANKING_SOFT_ID, bankingSoft, INSURANCE_SOFT_ID, insuranceSoft));
# +        //and
# +        bankingSoft.add(STASZEK_JAVA_MID);
# +
# +        //when
# +        Double result = simulationFacade.checkPotentialTransfer(projects, BANKING_SOFT_ID, INSURANCE_SOFT_ID, STASZEK_JAVA_MID, JAN_1);
# +
# +        //then
# +        assertEquals(81d, result);
# +    }
# +
# +    @Test
# +    void simulatesMovingCapabilitiesToDifferentProjectJustForAWhile() {
# +        //given
# +        Project bankingSoft =
# +                new Project(DEMAND_FOR_JAVA_MID_IN_JAN, valueOf(9));
# +        Project insuranceSoft =
# +                new Project(DEMAND_FOR_JAVA_JUST_FOR_15MIN_IN_JAN, valueOf(99));
# +        Projects projects = new Projects(
# +                Map.of(BANKING_SOFT_ID, bankingSoft, INSURANCE_SOFT_ID, insuranceSoft));
# +        //and
# +        bankingSoft.add(STASZEK_JAVA_MID);
# +
# +        //when
# +        Double result = simulationFacade.checkPotentialTransfer(projects, BANKING_SOFT_ID, INSURANCE_SOFT_ID, STASZEK_JAVA_MID, FIFTEEN_MINUTES_IN_JAN);
# +
# +        //then
# +        assertEquals(90d, result);
# +    }
# +
# +    @Test
# +    void theMoveGivesZeroProfitWhenThereAreStillMissingDemands() {
# +        //given
# +        Project bankingSoft =
# +                new Project(DEMAND_FOR_JAVA_MID_IN_JAN, valueOf(9));
# +        Project insuranceSoft =
# +                new Project(DEMANDS_FOR_JAVA_AND_PYTHON_IN_JAN, valueOf(99));
# +        Projects projects = new Projects(
# +                Map.of(BANKING_SOFT_ID, bankingSoft, INSURANCE_SOFT_ID, insuranceSoft));
# +        //and
# +        bankingSoft.add(STASZEK_JAVA_MID);
# +
# +        //when
# +        Double result = simulationFacade.checkPotentialTransfer(projects, BANKING_SOFT_ID, INSURANCE_SOFT_ID, STASZEK_JAVA_MID, JAN_1);
# +
# +        //then
# +        assertEquals(-9d, result);
# +    }
# +
# +}
