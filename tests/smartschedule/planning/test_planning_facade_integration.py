from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.planning_facade import PlanningFacade


class TestPlanningFacadeIntegration:
    def test_creates_project_and_loads_project_card(
        self, planning_facade: PlanningFacade
    ) -> None:
        project_id = planning_facade.add_new_project("project", Stage("Stage1"))

        loaded = planning_facade.load(project_id)

        assert loaded.project_id == project_id
        assert loaded.name == "project"
        assert str(loaded.parallelized_stages) == "Stage1"
