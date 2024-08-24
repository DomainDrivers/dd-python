from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.resource.employee.employee_id import EmployeeId
from smartschedule.resource.employee.seniority import Seniority
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.sqlalchemy_extensions import AsJSON, EmbeddedUUID, registry


@registry.mapped_as_dataclass()
class Employee:
    __tablename__ = "employees"

    id: Mapped[EmployeeId] = mapped_column(EmbeddedUUID[EmployeeId], primary_key=True)
    _version: Mapped[int] = mapped_column(name="version")
    name: Mapped[str]
    last_name: Mapped[str]
    seniority: Mapped[Seniority] = mapped_column(AsJSON[Seniority])
    _capabilities: Mapped[set[Capability]] = mapped_column(
        AsJSON[set[Capability]], name="capabilities"
    )

    __mapper_args__ = {"version_id_col": _version}

    def __init__(
        self,
        id: EmployeeId,
        name: str,
        last_name: str,
        status: Seniority,
        capabilities: set[Capability],
    ) -> None:
        self.id = id
        self.name = name
        self.last_name = last_name
        self.seniority = status
        self._capabilities = capabilities

    @property
    def capabilities(self) -> set[Capability]:
        return self._capabilities
