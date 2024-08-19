from __future__ import annotations

from dataclasses import dataclass

from smartschedule.shared.resource_name import ResourceName
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class ChosenResources:
    resources: set[ResourceName]
    time_slot: TimeSlot

    @staticmethod
    def none() -> ChosenResources:
        return ChosenResources(set(), TimeSlot.empty())
