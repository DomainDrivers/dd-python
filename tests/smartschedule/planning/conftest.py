import pytest
from lagom import Container

from smartschedule.planning.planning_facade import PlanningFacade


@pytest.fixture()
def planning_facade(container: Container) -> PlanningFacade:
    return container.resolve(PlanningFacade)
