import pytest

from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.parallelization.stage_parallelization import (
    StageParallelization,
)
from smartschedule.shared.resource_name import ResourceName

LEON = ResourceName("Leon")
ERYK = ResourceName("Eryk")
SLAWEK = ResourceName("Sławek")
KUBA = ResourceName("Kuba")


class TestParallelization:
    @pytest.fixture()
    def stage_parallelization(self) -> StageParallelization:
        return StageParallelization()

    def test_everything_can_be_done_in_parallel_if_there_are_no_dependencies(
        self, stage_parallelization: StageParallelization
    ) -> None:
        stage_1 = Stage("Stage1")
        stage_2 = Stage("Stage2")

        sorted_stages = stage_parallelization.of({stage_1, stage_2})

        assert len(sorted_stages.all) == 1

    def test_simple_dependencies(
        self, stage_parallelization: StageParallelization
    ) -> None:
        stage_1 = Stage("Stage1")
        stage_2 = Stage("Stage2")
        stage_3 = Stage("Stage3")
        stage_4 = Stage("Stage4")
        stage_2 = stage_2.depends_on(stage_1)
        stage_3 = stage_3.depends_on(stage_1)
        stage_4 = stage_4.depends_on(stage_2)

        sorted_stages = stage_parallelization.of({stage_1, stage_2, stage_3, stage_4})

        assert str(sorted_stages) == "Stage1 | Stage2, Stage3 | Stage4"

    def test_cant_be_done_when_there_is_a_cycle(
        self, stage_parallelization: StageParallelization
    ) -> None:
        stage_1 = Stage("Stage1")
        stage_2 = Stage("Stage2")
        stage_2 = stage_2.depends_on(stage_1)
        stage_1 = stage_1.depends_on(stage_2)  # making it cyclic

        sorted_stages = stage_parallelization.of({stage_1, stage_2})

        assert len(sorted_stages.all) == 0

    def test_takes_into_account_shared_resources(
        self, stage_parallelization: StageParallelization
    ) -> None:
        stage_1 = Stage("Stage1").with_chosen_resource_capabilities(LEON)
        stage_2 = Stage("Stage2").with_chosen_resource_capabilities(ERYK, LEON)
        stage_3 = Stage("Stage3").with_chosen_resource_capabilities(SLAWEK)
        stage_4 = Stage("Stage4").with_chosen_resource_capabilities(SLAWEK, KUBA)

        parallel_stages = stage_parallelization.of({stage_1, stage_2, stage_3, stage_4})

        assert str(parallel_stages) in [
            "Stage1, Stage3 | Stage2, Stage4",
            "Stage2, Stage4 | Stage1, Stage3",
        ]
