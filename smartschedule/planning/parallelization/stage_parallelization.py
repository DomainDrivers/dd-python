from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        return ParallelStagesList.empty()
