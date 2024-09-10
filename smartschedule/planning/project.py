from dataclasses import dataclass
from datetime import date

from smartschedule.planning.chosen_resources import ChosenResources
from smartschedule.planning.demands import Demands
from smartschedule.planning.demands_per_stage import DemandsPerStage
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass
class Project:
    id: ProjectId
    name: str
    parallelized_stages: ParallelStagesList
    demands_per_stage: DemandsPerStage
    all_demands: Demands
    chosen_resources: ChosenResources
    schedule: Schedule

    def __init__(self, name: str, parallelized_stages: ParallelStagesList) -> None:
        self.id = ProjectId.new_one()
        self.name = name
        self.parallelized_stages = parallelized_stages
        self.demands_per_stage = DemandsPerStage.empty()
        self.all_demands = Demands.none()
        self.chosen_resources = ChosenResources.none()
        self.schedule = Schedule.none()

    def add_demands(self, demands: Demands) -> None:
        self.all_demands = self.all_demands + demands

    def add_schedule(self, schedule: Schedule) -> None:
        self.schedule = schedule

    def add_schedule_by_start_date(self, possible_start_date: date) -> None:
        self.schedule = Schedule.based_on_start_day(
            possible_start_date, self.parallelized_stages
        )

    def add_schedule_by_critical_stage(
        self, critical_stage: Stage, stage_time_slot: TimeSlot
    ) -> None:
        self.schedule = Schedule.based_on_reference_stage_time_slots(
            critical_stage, stage_time_slot, self.parallelized_stages
        )

    def add_chosen_resources(self, needed_resources: ChosenResources) -> None:
        self.chosen_resources = needed_resources

    def add_demands_per_stage(self, demands_per_stage: DemandsPerStage) -> None:
        self.demands_per_stage = demands_per_stage
        unique_demands = set()
        for demands in demands_per_stage.demands.values():
            unique_demands.update(demands.all)
        self.add_demands(Demands(list(unique_demands)))

    def define_stages(self, parallelized_stages: ParallelStagesList) -> None:
        self.parallelized_stages = parallelized_stages
