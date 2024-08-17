from datetime import datetime, timezone

from smartschedule.shared.timeslot.time_slot import TimeSlot


class TestTimeSlot:
    def test_create_monthly_time_slot_at_utc(self) -> None:
        january_2023 = TimeSlot.create_monthly_time_slot_at_utc(2023, 1)

        assert january_2023.from_ == datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert january_2023.to == datetime(2023, 2, 1, 0, 0, 0, tzinfo=timezone.utc)

    def test_create_monthly_time_slot_in_december_at_utc(self) -> None:
        december_2024 = TimeSlot.create_monthly_time_slot_at_utc(2024, 12)

        assert december_2024.from_ == datetime(
            2024, 12, 1, 0, 0, 0, tzinfo=timezone.utc
        )
        assert december_2024.to == datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    def test_create_daily_time_slot_at_utc(self) -> None:
        specific_day = TimeSlot.create_daily_time_slot_at_utc(2023, 1, 15)

        assert specific_day.from_ == datetime(2023, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        assert specific_day.to == datetime(2023, 1, 16, 0, 0, 0, tzinfo=timezone.utc)

    def test_one_slot_within_another(self) -> None:
        slot1 = TimeSlot(
            from_=datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 2, 23, 59, 59, tzinfo=timezone.utc),
        )
        slot2 = TimeSlot(
            from_=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
        )

        assert slot1.within(slot2)
        assert not slot2.within(slot1)

    def test_one_slot_is_not_within_another_if_they_just_overlap(self) -> None:
        slot1 = TimeSlot(
            from_=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 2, 23, 59, 59, tzinfo=timezone.utc),
        )
        slot2 = TimeSlot(
            from_=datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
        )

        assert not slot1.within(slot2)
        assert not slot2.within(slot1)

        slot3 = TimeSlot(
            from_=datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 3, 23, 59, 59, tzinfo=timezone.utc),
        )
        slot4 = TimeSlot(
            from_=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 2, 23, 59, 59, tzinfo=timezone.utc),
        )

        assert not slot3.within(slot4)
        assert not slot4.within(slot3)

    def test_slot_is_not_within_another_when_they_are_completely_outside(self) -> None:
        slot1 = TimeSlot(
            from_=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 1, 23, 59, 59, tzinfo=timezone.utc),
        )
        slot2 = TimeSlot(
            from_=datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
        )

        assert not slot1.within(slot2)
        assert not slot2.within(slot1)

    def test_slot_is_within_itself(self) -> None:
        slot1 = TimeSlot(
            from_=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            to=datetime(2023, 1, 1, 23, 59, 59, tzinfo=timezone.utc),
        )

        assert slot1.within(slot1)
