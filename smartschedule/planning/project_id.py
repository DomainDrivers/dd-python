from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ProjectId:
    uuid: UUID

    @property
    def id(self) -> UUID:
        return self.uuid

    @staticmethod
    def new_one() -> ProjectId:
        return ProjectId(uuid4())
