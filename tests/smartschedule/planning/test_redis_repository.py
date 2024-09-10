from datetime import datetime
from typing import Final

import pytest
from lagom import Container

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.chosen_resources import ChosenResources
from smartschedule.planning.demand import Demand
from smartschedule.planning.demands import Demands
from smartschedule.planning.demands_per_stage import DemandsPerStage
from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.project import Project
from smartschedule.planning.redis_project_repository import RedisProjectRepository
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.timeslot.time_slot import TimeSlot


@pytest.fixture()
def repository(container: Container) -> RedisProjectRepository:
    return container.resolve(RedisProjectRepository)


class TestRedisRepository:
    JAN_10_20: Final = TimeSlot(datetime(2020, 1, 10), datetime(2020, 1, 20))
    NEEDED_RESOURCES: Final = ChosenResources({ResourceId.new_one()}, JAN_10_20)
    SCHEDULE: Final = Schedule({"Stage1": JAN_10_20})
    DEMAND_FOR_JAVA: Final = Demands.of(Demand(Capability.skill("Java")))
    DEMANDS_PER_STAGE: Final = DemandsPerStage.empty()
    STAGES: Final = ParallelStagesList.of(ParallelStages({Stage("Stage1")}))

    def test_can_save_and_load_project(
        self, repository: RedisProjectRepository
    ) -> None:
        project = Project("project", self.STAGES)
        project.add_schedule(self.SCHEDULE)
        project.add_demands(self.DEMAND_FOR_JAVA)
        project.add_chosen_resources(self.NEEDED_RESOURCES)
        project.add_demands_per_stage(self.DEMANDS_PER_STAGE)
        repository.save(project)

        loaded = repository.get(project.id)

        assert loaded.chosen_resources == self.NEEDED_RESOURCES
        assert loaded.parallelized_stages == self.STAGES
        assert loaded.schedule == self.SCHEDULE
        assert loaded.all_demands == self.DEMAND_FOR_JAVA
        assert loaded.demands_per_stage == self.DEMANDS_PER_STAGE

    def test_loads_multiple_projects(self, repository: RedisProjectRepository) -> None:
        project = Project("project", self.STAGES)
        project2 = Project("project2", self.STAGES)
        repository.save(project)
        repository.save(project2)

        loaded = repository.get_all([project.id, project2.id])

        assert len(loaded) == 2
        assert {p.id for p in loaded} == {project.id, project2.id}

    def test_loads_all_projects(self, repository: RedisProjectRepository) -> None:
        project = Project("project", self.STAGES)
        project2 = Project("project2", self.STAGES)
        repository.save(project)
        repository.save(project2)

        loaded = repository.get_all()

        assert len(loaded) == 2
        assert {p.id for p in loaded} == {project.id, project2.id}
