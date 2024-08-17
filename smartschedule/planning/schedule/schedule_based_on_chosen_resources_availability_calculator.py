import functools
from datetime import timedelta

from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.schedule.calendars import Calendars
from smartschedule.shared.timeslot.time_slot import TimeSlot


class ScheduleBasedOnChosenResourcesAvailabilityCalculator:
    def calculate(
        self, chosen_resources_calendars: Calendars, stages: list[Stage]
    ) -> dict[str, TimeSlot]:
        schedule = {}
        for stage in stages:
            proposed_slot = self._find_slot_for_stage(chosen_resources_calendars, stage)
            if proposed_slot == TimeSlot.empty():
                return {}
            schedule[stage.name] = proposed_slot
        return schedule

    def _find_slot_for_stage(
        self, chosen_resources_calendars: Calendars, stage: Stage
    ) -> TimeSlot:
        found_slots = self._possible_slots(chosen_resources_calendars, stage)
        if TimeSlot.empty() in found_slots:
            return TimeSlot.empty()

        common_slot_for_all_resources = self._find_common_part_of_slots(found_slots)

        while not self._is_slot_long_enough_for_stage(
            stage, common_slot_for_all_resources
        ):
            common_slot_for_all_resources = common_slot_for_all_resources.stretch(
                timedelta(days=1)
            )

        return TimeSlot(
            common_slot_for_all_resources.from_,
            common_slot_for_all_resources.from_ + stage.duration,
        )

    def _is_slot_long_enough_for_stage(self, stage: Stage, slot: TimeSlot) -> bool:
        return slot.duration >= stage.duration

    def _find_common_part_of_slots(self, found_slots: list[TimeSlot]) -> TimeSlot:
        return functools.reduce(TimeSlot.common_part_with, found_slots)

    def _possible_slots(
        self, chosen_resources_calendars: Calendars, stage: Stage
    ) -> list[TimeSlot]:
        result = []
        for resource in stage.resources:
            calendar = chosen_resources_calendars.get(resource)
            matching_slots = [
                slot
                for slot in calendar.available_slots()
                if self._is_slot_long_enough_for_stage(stage, slot)
            ]

            matching_slot = next(iter(matching_slots), TimeSlot.empty())
            result.append(matching_slot)

        return result
