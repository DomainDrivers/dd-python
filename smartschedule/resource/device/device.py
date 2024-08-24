from sqlalchemy.orm import Mapped, mapped_column

from smartschedule.resource.device.device_id import DeviceId
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.sqlalchemy_extensions import AsJSON, EmbeddedUUID, registry


@registry.mapped_as_dataclass()
class Device:
    __tablename__ = "devices"

    id: Mapped[DeviceId] = mapped_column(EmbeddedUUID[DeviceId], primary_key=True)
    _version: Mapped[int] = mapped_column(name="version")
    model: Mapped[str]
    _capabilities: Mapped[set[Capability]] = mapped_column(
        AsJSON[set[Capability]], name="capabilities"
    )

    __mapper_args__ = {"version_id_col": _version}

    def __init__(self, id: DeviceId, model: str, capabilities: set[Capability]) -> None:
        self.id = id
        self.model = model
        self._capabilities = capabilities

    @property
    def capabilities(self) -> set[Capability]:
        return self._capabilities
