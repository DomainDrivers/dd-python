from __future__ import annotations
from dataclasses import dataclass

from smartschedule.planning.parallelization.parallel_stages import ParallelStages


@dataclass
class ParallelStagesList:
    all: list[ParallelStages]

    @classmethod
    def empty(cls) -> ParallelStagesList:
        return ParallelStagesList([])

    def add(self, parallel_stages: ParallelStages) -> ParallelStagesList:
        concatenated_lists = self.all + [parallel_stages]
        return ParallelStagesList(concatenated_lists)

    def __str__(self) -> str:
        return " | ".join([str(parallel_stages) for parallel_stages in self.all])
