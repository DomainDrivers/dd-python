from datetime import date, datetime, timedelta

import pytest

from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.resource_name import ResourceName
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.schedule.calendars import Calendar, Calendars
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.schedule.assertions.schedule_assert import (
    ScheduleAssert,
)


@pytest.fixture()
def jan_1() -> date:
    return date(2020, 1, 1)


@pytest.fixture()
def jan_10_20() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 10), datetime(2020, 1, 20))


@pytest.fixture()
def jan_1_1() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 2))


@pytest.fixture()
def jan_3_10() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 3), datetime(2020, 1, 10))


@pytest.fixture()
def jan_1_20() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 20))


@pytest.fixture()
def jan_11_21() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 11), datetime(2020, 1, 21))


@pytest.fixture()
def jan_1_4() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 4))


@pytest.fixture()
def jan_4_14() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 4), datetime(2020, 1, 14))


@pytest.fixture()
def jan_14_16() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 14), datetime(2020, 1, 16))


@pytest.fixture()
def jan_1_5() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 5))


@pytest.fixture()
def dec_29_jan_1() -> TimeSlot:
    return TimeSlot(datetime(2019, 12, 29), datetime(2020, 1, 1))


@pytest.fixture()
def jan_1_11() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 1), datetime(2020, 1, 11))


@pytest.fixture()
def jan_5_7() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 5), datetime(2020, 1, 7))


@pytest.fixture()
def jan_3_6() -> TimeSlot:
    return TimeSlot(datetime(2020, 1, 3), datetime(2020, 1, 6))


class TestScheduleCalculation:
    @pytest.mark.xfail(reason="Not implemented yet", strict=True)
    def test_calculate_schedule_based_on_the_start_day(
        self, jan_1: date, jan_1_4: TimeSlot, jan_4_14: TimeSlot, jan_14_16: TimeSlot
    ) -> None:
        stage1 = Stage("Stage1").of_duration(timedelta(days=3))
        stage2 = Stage("Stage2").of_duration(timedelta(days=10))
        stage3 = Stage("Stage3").of_duration(timedelta(days=2))

        parallel_stages = ParallelStagesList.of(
            ParallelStages.of(stage1),
            ParallelStages.of(stage2),
            ParallelStages.of(stage3),
        )

        schedule = Schedule.based_on_start_day(jan_1, parallel_stages)

        schedule_assert = ScheduleAssert(schedule)
        schedule_assert.assert_has_stage("Stage1").assert_with_slot(jan_1_4)
        schedule_assert.assert_has_stage("Stage2").assert_with_slot(jan_4_14)
        schedule_assert.assert_has_stage("Stage3").assert_with_slot(jan_14_16)

    def test_can_adjust_to_dates_of_one_reference_stage(
        self,
        jan_1_5: TimeSlot,
        dec_29_jan_1: TimeSlot,
        jan_1_11: TimeSlot,
        jan_5_7: TimeSlot,
    ) -> None:
        stage = Stage("S1").of_duration(timedelta(days=3))
        another_stage = Stage("S2").of_duration(timedelta(days=10))
        yet_another_stage = Stage("S3").of_duration(timedelta(days=2))
        reference_stage = Stage("S4-Reference").of_duration(timedelta(days=4))

        parallel_stages = ParallelStagesList.of(
            ParallelStages.of(stage),
            ParallelStages.of(reference_stage, another_stage),
            ParallelStages.of(yet_another_stage),
        )

        schedule = Schedule.based_on_reference_stage_time_slots(
            reference_stage, jan_1_5, parallel_stages
        )

        schedule_assert = ScheduleAssert(schedule)
        schedule_assert.assert_has_stage("S1").assert_with_slot(
            dec_29_jan_1
        ).assert_is_before("S4-Reference")
        schedule_assert.assert_has_stage("S2").assert_with_slot(
            jan_1_11
        ).assert_starts_together_with("S4-Reference")
        schedule_assert.assert_has_stage("S3").assert_with_slot(
            jan_5_7
        ).assert_is_after("S4-Reference")
        schedule_assert.assert_has_stage("S4-Reference").assert_with_slot(jan_1_5)

    def test_no_schedule_is_calculated_if_reference_stage_to_adjust_to_does_not_exists(
        self, jan_1_5: TimeSlot
    ) -> None:
        stage1 = Stage("Stage1").of_duration(timedelta(days=3))
        stage2 = Stage("Stage2").of_duration(timedelta(days=10))
        stage3 = Stage("Stage3").of_duration(timedelta(days=2))
        stage4 = Stage("Stage4").of_duration(timedelta(days=4))

        parallel_stages = ParallelStagesList.of(
            ParallelStages.of(stage1),
            ParallelStages.of(stage2, stage4),
            ParallelStages.of(stage3),
        )

        schedule = Schedule.based_on_reference_stage_time_slots(
            Stage("Stage5"), jan_1_5, parallel_stages
        )

        assert schedule == Schedule.none()

    def test_adjusts_schedule_to_availability_of_needed_resources(
        self,
        jan_1_1: TimeSlot,
        jan_3_10: TimeSlot,
        jan_1_20: TimeSlot,
        jan_11_21: TimeSlot,
        jan_3_6: TimeSlot,
        jan_10_20: TimeSlot,
    ) -> None:
        r1 = ResourceName("r1")
        r2 = ResourceName("r2")
        r3 = ResourceName("r3")

        stage1 = (
            Stage("Stage1")
            .of_duration(timedelta(days=3))
            .with_chosen_resource_capabilities(r1)
        )
        stage2 = (
            Stage("Stage2")
            .of_duration(timedelta(days=10))
            .with_chosen_resource_capabilities(r2, r3)
        )

        cal1 = Calendar.with_available_slots(r1, jan_1_1, jan_3_10)
        cal2 = Calendar.with_available_slots(r2, jan_1_20)
        cal3 = Calendar.with_available_slots(r3, jan_11_21)

        schedule = Schedule.based_on_chosen_resource_availability(
            Calendars.of(cal1, cal2, cal3), [stage1, stage2]
        )

        schedule_assert = ScheduleAssert(schedule)
        schedule_assert.assert_has_stage("Stage1").assert_with_slot(jan_3_6)
        schedule_assert.assert_has_stage("Stage2").assert_with_slot(jan_10_20)
