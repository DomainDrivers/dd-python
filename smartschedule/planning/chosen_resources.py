from __future__ import annotations

from dataclasses import dataclass

from smartschedule.availability.resource_id import ResourceId
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class ChosenResources:
    resources: set[ResourceId]
    time_slot: TimeSlot

    @staticmethod
    def none() -> ChosenResources:
        return ChosenResources(set(), TimeSlot.empty())
