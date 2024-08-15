from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.sorted_nodes_to_parallelized_stages import (
    SortedNodesToParallelizedStages,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.parallelization.stages_to_nodes import StagesToNodes
from smartschedule.sorter.graph_topological_sort import GraphTopologicalSort


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        nodes = StagesToNodes().calculate(list(stages))
        sorted_nodes = GraphTopologicalSort[Stage]().sort(nodes)
        return SortedNodesToParallelizedStages().calculate(sorted_nodes)
