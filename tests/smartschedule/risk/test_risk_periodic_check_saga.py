from datetime import datetime, timedelta, timezone
from typing import Final, Iterator

import pytest
import time_machine

from smartschedule.allocation.capabilityscheduling.allocatable_capability_id import (
    AllocatableCapabilityId,
)
from smartschedule.allocation.cashflow.earnings import Earnings
from smartschedule.allocation.cashflow.earnings_recalculated import EarningsRecalculated
from smartschedule.allocation.demand import Demand
from smartschedule.allocation.demands import Demands
from smartschedule.allocation.project_allocation_scheduled import (
    ProjectAllocationScheduled,
)
from smartschedule.allocation.project_allocations_id import ProjectAllocationsId
from smartschedule.availability.owner import Owner
from smartschedule.availability.resource_taken_over import ResourceTakenOver
from smartschedule.risk.risk_periodic_check_saga import RiskPeriodicCheckSaga
from smartschedule.risk.risk_periodic_check_saga_step import RiskPeriodicCheckSagaStep
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestRiskPeriodicCheckSaga:
    JAVA: Final = Capability.skill("JAVA")
    ONE_DAY: Final = TimeSlot.create_daily_time_slot_at_utc(2021, 1, 1)
    SINGLE_DEMAND: Final = Demands.of(Demand(JAVA, ONE_DAY))
    MANY_DEMANDS: Final = Demands.of(Demand(JAVA, ONE_DAY), Demand(JAVA, ONE_DAY))
    PROJECT_DATES: Final = TimeSlot(
        datetime(2021, 1, 1, tzinfo=timezone.utc),
        datetime(2021, 1, 5, tzinfo=timezone.utc),
    )
    PROJECT_ID: Final = ProjectAllocationsId.new_one()
    CAPABILITY_ID: Final = AllocatableCapabilityId.new_one()

    @pytest.fixture(autouse=True)
    def freeze_time(self) -> Iterator[None]:
        with time_machine.travel(datetime.now(tz=timezone.utc), tick=False):
            yield

    def test_updates_missing_demands_on_saga_creation(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        assert saga.missing_demands == self.SINGLE_DEMAND

    def test_updates_deadline_on_deadline_set(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        assert saga.deadline == self.PROJECT_DATES.to

    def test_updates_missing_demands(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.set_missing_demands(self.MANY_DEMANDS)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING
        assert saga.missing_demands == self.MANY_DEMANDS

    def test_no_new_steps_on_when_missing_demands(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)

        next_step = saga.set_missing_demands(self.MANY_DEMANDS)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_updated_earnings_on_earnings_recalculated(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )
        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

        assert saga.earnings == Earnings(1000)

        next_step = saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(900), datetime.now())
        )

        assert saga.earnings == Earnings(900)
        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_informs_about_demands_satisfied_when_no_missing_demands(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )

        still_missing = saga.set_missing_demands(self.SINGLE_DEMAND)
        zero_demands = saga.set_missing_demands(Demands.none())

        assert still_missing == RiskPeriodicCheckSagaStep.DO_NOTHING
        assert zero_demands == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_DEMANDS_SATISFIED

    def test_do_nothing_on_resource_taken_over_when_after_deadline(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        after_deadline = self.PROJECT_DATES.to + timedelta(hours=100)
        next_step = saga.handle(
            ResourceTakenOver(
                self.CAPABILITY_ID.to_availability_resource_id(),
                {Owner(self.PROJECT_ID.id)},
                self.ONE_DAY,
                after_deadline,
            )
        )

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_notify_about_risk_on_resource_taken_over_when_before_deadline(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        before_deadline = self.PROJECT_DATES.to - timedelta(hours=100)
        next_step = saga.handle(
            ResourceTakenOver(
                self.CAPABILITY_ID.to_availability_resource_id(),
                {Owner(self.PROJECT_ID.id)},
                self.ONE_DAY,
                before_deadline,
            )
        )

        assert next_step == RiskPeriodicCheckSagaStep.NOTIFY_ABOUT_POSSIBLE_RISK

    def test_no_next_step_on_capability_released(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.set_missing_demands(self.SINGLE_DEMAND)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_should_result_in_nothing_when_all_demands_satisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )
        saga.set_missing_demands(Demands.none())
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        way_before_deadline = self.PROJECT_DATES.to - timedelta(days=1)
        next_step = saga.handle_weekly_check(way_before_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_handle_weekly_check_should_result_in_nothing_when_after_deadline(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        way_after_deadline = self.PROJECT_DATES.to + timedelta(days=300)
        next_step = saga.handle_weekly_check(way_after_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_does_nothing_when_no_deadline(self) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)

        next_step = saga.handle_weekly_check(datetime.now())

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_results_in_nothing_when_not_close_to_deadline_and_demands_unsatisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.SINGLE_DEMAND)
        saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        way_before_deadline = self.PROJECT_DATES.to - timedelta(days=300)
        next_step = saga.handle_weekly_check(way_before_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.DO_NOTHING

    def test_weekly_check_should_result_in_find_available_when_close_to_deadline_and_demands_not_satisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        close_to_deadline = self.PROJECT_DATES.to - timedelta(days=20)
        next_step = saga.handle_weekly_check(close_to_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.FIND_AVAILABLE

    def test_weekly_check_should_result_in_replacement_suggesting_when_hihgh_value_project_really_close_to_deadline_and_demands_not_satisfied(
        self,
    ) -> None:
        saga = RiskPeriodicCheckSaga(self.PROJECT_ID, self.MANY_DEMANDS)
        saga.handle(
            EarningsRecalculated(self.PROJECT_ID, Earnings(1000), datetime.now())
        )
        saga.handle(
            ProjectAllocationScheduled(
                self.PROJECT_ID, self.PROJECT_DATES, datetime.now()
            )
        )

        really_close_to_deadline = self.PROJECT_DATES.to - timedelta(days=2)
        next_step = saga.handle_weekly_check(really_close_to_deadline)

        assert next_step == RiskPeriodicCheckSagaStep.SUGGEST_REPLACEMENT
