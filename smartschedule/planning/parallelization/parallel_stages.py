from dataclasses import dataclass

from smartschedule.planning.parallelization.stage import Stage


@dataclass
class ParallelStages:
    stages: set[Stage]

    def __str__(self) -> str:
        sorted_stages = sorted(self.stages, key=lambda stage: stage.name)
        return ", ".join([str(stage) for stage in sorted_stages])
