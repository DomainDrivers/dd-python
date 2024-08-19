from dataclasses import dataclass

from smartschedule.planning.chosen_resources import ChosenResources
from smartschedule.planning.demands import Demands
from smartschedule.planning.demands_per_stage import DemandsPerStage
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.schedule.schedule import Schedule


@dataclass(frozen=True)
class ProjectCard:
    project_id: ProjectId
    name: str
    parallelized_stages: ParallelStagesList
    demands: Demands
    schedule: Schedule
    demands_per_stage: DemandsPerStage
    needed_resources: ChosenResources
