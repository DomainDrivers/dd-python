from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class RiskPeriodicCheckSagaId:
    _project_risk_saga_id: UUID

    @property
    def id(self) -> UUID:
        return self._project_risk_saga_id

    @staticmethod
    def new_one() -> RiskPeriodicCheckSagaId:
        return RiskPeriodicCheckSagaId(uuid4())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RiskPeriodicCheckSagaId):
            return False
        return self._project_risk_saga_id == other._project_risk_saga_id

    def __hash__(self) -> int:
        return hash(self._project_risk_saga_id)

    def __repr__(self) -> str:
        return f"RiskPeriodicCheckSagaId(UUID(hex='{self._project_risk_saga_id}'))"

    def __str__(self) -> str:
        return str(self._project_risk_saga_id)

    def __lt__(self, other: RiskPeriodicCheckSagaId) -> bool:
        return self._project_risk_saga_id < other._project_risk_saga_id
