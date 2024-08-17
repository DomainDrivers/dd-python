from dataclasses import dataclass

from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class Demand:
    capability: Capability
    time_slot: TimeSlot
