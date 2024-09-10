from datetime import date, datetime, timedelta
from typing import Any

import pytest
from lagom import Container
from mockito import verify  # type: ignore
from mockito.matchers import arg_that  # type: ignore

from smartschedule.availability.resource_id import ResourceId
from smartschedule.planning.capabilities_demanded import CapabilitiesDemanded
from smartschedule.planning.chosen_resources import ChosenResources
from smartschedule.planning.demand import Demand
from smartschedule.planning.demands import Demands
from smartschedule.planning.demands_per_stage import DemandsPerStage
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.planning.schedule.schedule import Schedule
from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.event_bus import EventBus
from smartschedule.shared.timeslot.time_slot import TimeSlot
from tests.smartschedule.planning.in_memory_project_repository import (
    InMemoryProjectRepository,
)


@pytest.fixture(autouse=True)
def container(container: Container) -> Container:
    test_container = container.clone()
    test_container[ProjectRepository] = InMemoryProjectRepository()  # type: ignore[type-abstract]
    return test_container


class TestPlanningFacade:
    def test_can_create_project_and_load_project_card(
        self, planning_facade: PlanningFacade
    ) -> None:
        project_id = planning_facade.add_new_project("project", Stage("Stage 1"))

        project_card = planning_facade.load(project_id)

        assert project_card.project_id == project_id
        assert project_card.name == "project"
        assert str(project_card.parallelized_stages) == "Stage 1"

    def test_loads_multiple_projects(self, planning_facade: PlanningFacade) -> None:
        project_id_1 = planning_facade.add_new_project("project 1", Stage("Stage 1"))
        project_id_2 = planning_facade.add_new_project("project 2", Stage("Stage 2"))

        loaded = planning_facade.load_all(project_id_1, project_id_2)

        assert {project.project_id for project in loaded} == {
            project_id_1,
            project_id_2,
        }

    def test_creates_and_saves_more_complex_parallelization(
        self, planning_facade: PlanningFacade
    ) -> None:
        stage_1 = Stage("Stage1")
        stage_2 = Stage("Stage2")
        stage_3 = Stage("Stage3")
        stage_2 = stage_2.depends_on(stage_1)
        stage_3 = stage_3.depends_on(stage_2)
        project_id = planning_facade.add_new_project(
            "project", stage_1, stage_2, stage_3
        )

        loaded = planning_facade.load(project_id)

        assert str(loaded.parallelized_stages) == "Stage1 | Stage2 | Stage3"

    def test_plan_demands(self, planning_facade: PlanningFacade) -> None:
        project_id = planning_facade.add_new_project("project", Stage("Stage 1"))

        demands_for_java = Demands.of(Demand.for_(Capability.skill("JAVA")))
        planning_facade.add_demands(project_id, demands_for_java)

        loaded = planning_facade.load(project_id)
        assert loaded.demands == demands_for_java

    def test_plans_new_demands(self, planning_facade: PlanningFacade) -> None:
        project_id = planning_facade.add_new_project("project", Stage("Stage 1"))

        java_demand = Demand.for_(Capability.skill("JAVA"))
        python_demand = Demand.for_(Capability.skill("PYTHON"))
        planning_facade.add_demands(project_id, Demands.of(java_demand))
        planning_facade.add_demands(project_id, Demands.of(python_demand))

        loaded = planning_facade.load(project_id)
        assert loaded.demands == Demands.of(java_demand, python_demand)

    def test_plans_demands_per_stage(self, planning_facade: PlanningFacade) -> None:
        stage = Stage("Stage 1")
        project_id = planning_facade.add_new_project("project", stage)

        demands_for_java = Demands.of(Demand.for_(Capability.skill("JAVA")))
        demands_per_stage = DemandsPerStage({stage.name: demands_for_java})
        planning_facade.define_demands_per_stage(project_id, demands_per_stage)

        loaded = planning_facade.load(project_id)
        assert loaded.demands_per_stage == demands_per_stage
        assert loaded.demands == demands_for_java

    def test_plans_needed_resources_in_time(
        self, planning_facade: PlanningFacade
    ) -> None:
        project_id = planning_facade.add_new_project("project")

        needed_resources = {ResourceId.new_one()}
        first_half_of_the_year = TimeSlot(
            from_=datetime(2022, 1, 1), to=datetime(2022, 6, 30)
        )
        planning_facade.define_resources_within_dates(
            project_id, needed_resources, first_half_of_the_year
        )

        loaded = planning_facade.load(project_id)
        assert loaded.needed_resources == ChosenResources(
            needed_resources, first_half_of_the_year
        )

    def test_redefines_stages(self, planning_facade: PlanningFacade) -> None:
        project_id = planning_facade.add_new_project("project", Stage("Stage 1"))

        planning_facade.define_project_stages(project_id, Stage("Stage 2"))

        loaded = planning_facade.load(project_id)
        assert str(loaded.parallelized_stages) == "Stage 2"

    def test_calculates_schedule_after_passing_possible_start(
        self, planning_facade: PlanningFacade
    ) -> None:
        stage_1 = Stage("Stage1", duration=timedelta(days=2))
        stage_2 = Stage("Stage2", duration=timedelta(days=5))
        stage_3 = Stage("Stage3", duration=timedelta(days=7))
        project_id = planning_facade.add_new_project(
            "project", stage_1, stage_2, stage_3
        )

        planning_facade.define_start_date(project_id, date(2021, 1, 1))

        loaded = planning_facade.load(project_id)
        assert loaded.schedule.dates == {
            "Stage1": TimeSlot(from_=datetime(2021, 1, 1), to=datetime(2021, 1, 3)),
            "Stage2": TimeSlot(from_=datetime(2021, 1, 1), to=datetime(2021, 1, 6)),
            "Stage3": TimeSlot(from_=datetime(2021, 1, 1), to=datetime(2021, 1, 8)),
        }

    def test_adding_schedule_manually(self, planning_facade: PlanningFacade) -> None:
        stage_1 = Stage("Stage1", duration=timedelta(days=2))
        stage_2 = Stage("Stage2", duration=timedelta(days=5))
        stage_3 = Stage("Stage3", duration=timedelta(days=7))
        project_id = planning_facade.add_new_project(
            "project", stage_1, stage_2, stage_3
        )

        dates = {
            "Stage1": TimeSlot(from_=datetime(2021, 1, 1), to=datetime(2021, 1, 3)),
            "Stage2": TimeSlot(from_=datetime(2021, 1, 1), to=datetime(2021, 1, 6)),
            "Stage3": TimeSlot(from_=datetime(2021, 1, 1), to=datetime(2021, 1, 8)),
        }
        schedule = Schedule(dates)
        planning_facade.define_manual_schedule(project_id, schedule)

        loaded = planning_facade.load(project_id)
        assert loaded.schedule.dates == dates

    def test_capabilities_demanded_event_is_emitted_after_adding_demands(
        self, planning_facade: PlanningFacade, when: Any
    ) -> None:
        when(EventBus).publish(...)
        project_id = planning_facade.add_new_project("project", Stage("Stage 1"))
        demands_for_java = Demands.of(Demand.for_(Capability.skill("JAVA")))

        planning_facade.add_demands(project_id, demands_for_java)

        verify(EventBus).publish(
            arg_that(
                lambda event: self._is_capabilities_demanded(
                    event, project_id, demands_for_java
                )
            )
        )

    def _is_capabilities_demanded(
        self, event: Any, project_id: Any, demands: Any
    ) -> bool:
        return (
            isinstance(event, CapabilitiesDemanded)
            and event.project_id == project_id
            and event.demands == demands
        )
