from itertools import chain

from smartschedule.allocation.capabilityscheduling.legacyacl.employee_data_from_legacy_esb_message import (
    EmployeeDataFromLegacyEsbMessage,
)
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import CapabilitySelector


def translate(message: EmployeeDataFromLegacyEsbMessage) -> list[CapabilitySelector]:
    employee_skills = [
        CapabilitySelector.can_perform_all_at_the_time(
            {Capability.skill(skill_name) for skill_name in skill_names}
        )
        for skill_names in message.skills_performed_together
    ]
    employee_exclusive_skills = [
        CapabilitySelector.can_just_perform(Capability.skill(skill_name))
        for skill_name in message.exclusive_skills
    ]
    employee_permissions = list(
        chain.from_iterable(
            _multiple_permissions(permission) for permission in message.permissions
        )
    )

    return employee_skills + employee_exclusive_skills + employee_permissions


def _multiple_permissions(permission_legacy_code: str) -> list[CapabilitySelector]:
    parts = permission_legacy_code.split("<>")
    permission = parts[0]
    times = int(parts[1])
    return [
        CapabilitySelector.can_just_perform(Capability.permission(permission))
        for _ in range(times)
    ]
