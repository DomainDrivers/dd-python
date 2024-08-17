from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from smartschedule.planning.parallelization.stage import Stage


@dataclass
class ParallelStages:
    stages: set[Stage]

    @staticmethod
    def of(*stages: Stage) -> ParallelStages:
        return ParallelStages(set(stages))

    @property
    def duration(self) -> timedelta:
        return max([stage.duration for stage in self.stages], default=timedelta())

    def __str__(self) -> str:
        sorted_stages = sorted(self.stages, key=lambda stage: stage.name)
        return ", ".join([str(stage) for stage in sorted_stages])
