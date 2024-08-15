from returns.pipeline import flow

from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.sorted_nodes_to_parallelized_stages import (
    sorted_nodes_to_parallelized_stages,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.parallelization.stages_to_nodes import stages_to_nodes
from smartschedule.sorter.graph_topological_sort import graph_topological_sort


class StageParallelization:

    def of(self, stages: set[Stage]) -> ParallelStagesList:
        return flow(
            stages,
            list,
            stages_to_nodes,
            graph_topological_sort,
            sorted_nodes_to_parallelized_stages,
        )
