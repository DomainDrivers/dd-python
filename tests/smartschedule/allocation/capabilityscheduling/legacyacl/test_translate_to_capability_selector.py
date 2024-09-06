import factory  # type: ignore

from smartschedule.allocation.capabilityscheduling.legacyacl.employee_data_from_legacy_esb_message import (
    EmployeeDataFromLegacyEsbMessage,
)
from smartschedule.allocation.capabilityscheduling.legacyacl.translate_to_capability_selector import (
    translate,
)
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import CapabilitySelector
from smartschedule.shared.timeslot.time_slot import TimeSlot


class EmployeeDataFromLegacyEsbMessageFactory(factory.Factory):  # type: ignore
    class Meta:
        model = EmployeeDataFromLegacyEsbMessage

    resource_id = factory.Faker("uuid4")
    skills_performed_together = factory.LazyFunction(list)
    exclusive_skills = factory.LazyFunction(list)
    permissions = factory.LazyFunction(list)
    time_slot = TimeSlot.empty()


class TestTranslateToCapabilitySelector:
    def test_translate_legacy_esb_message_to_capability_selector_model(self) -> None:
        legacy_permissions = ["ADMIN<>2", "ROOT<>1"]
        legacy_skills_performed_together = [
            ["JAVA", "CSHARP", "PYTHON"],
            ["RUST", "CSHARP", "PYTHON"],
        ]
        legacy_exclusive_skills = ["YT DRAMA COMMENTS"]
        message = EmployeeDataFromLegacyEsbMessageFactory(
            permissions=legacy_permissions,
            skills_performed_together=legacy_skills_performed_together,
            exclusive_skills=legacy_exclusive_skills,
        )

        result = translate(message)

        assert len(result) == 6
        assert (
            result.count(
                CapabilitySelector.can_perform_one_of({Capability.permission("ADMIN")})
            )
            == 2
        )
        assert set(result) == {
            CapabilitySelector.can_perform_one_of(
                {Capability.skill("YT DRAMA COMMENTS")}
            ),
            CapabilitySelector.can_perform_all_at_the_time(
                Capability.skills("JAVA", "CSHARP", "PYTHON")
            ),
            CapabilitySelector.can_perform_all_at_the_time(
                Capability.skills("RUST", "CSHARP", "PYTHON")
            ),
            CapabilitySelector.can_perform_one_of({Capability.permission("ADMIN")}),
            CapabilitySelector.can_perform_one_of({Capability.permission("ROOT")}),
        }

    def test_zero_means_no_permission_nowhere(self) -> None:
        legacy_permissions = ["ADMIN<>0"]
        message = EmployeeDataFromLegacyEsbMessageFactory(
            permissions=legacy_permissions
        )

        result = translate(message)

        assert len(result) == 0
