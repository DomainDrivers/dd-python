from __future__ import annotations

from dataclasses import dataclass

from smartschedule.planning.demands import Demands


@dataclass(frozen=True)
class DemandsPerStage:
    demands: dict[str, Demands]

    @staticmethod
    def empty() -> DemandsPerStage:
        return DemandsPerStage({})
