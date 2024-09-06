from dataclasses import dataclass
from uuid import UUID

from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class EmployeeDataFromLegacyEsbMessage:
    resource_id: UUID
    skills_performed_together: list[list[str]]
    exclusive_skills: list[str]
    permissions: list[str]
    time_slot: TimeSlot
