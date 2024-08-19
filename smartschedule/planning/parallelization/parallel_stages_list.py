from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.shared.typing_extensions import Comparable


@dataclass
class ParallelStagesList:
    all: list[ParallelStages]

    @staticmethod
    def of(*parallel_stages: ParallelStages) -> ParallelStagesList:
        return ParallelStagesList(list(parallel_stages))

    def add(self, parallel_stages: ParallelStages) -> ParallelStagesList:
        concatenated_lists = self.all + [parallel_stages]
        return ParallelStagesList(concatenated_lists)

    def all_sorted(
        self, sort_key_getter: Callable[[ParallelStages], Comparable]
    ) -> list[ParallelStages]:
        return sorted(self.all, key=sort_key_getter)

    def __str__(self) -> str:
        return " | ".join([str(parallel_stages) for parallel_stages in self.all])
