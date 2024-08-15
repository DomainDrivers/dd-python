from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.sorter.sorted_nodes import SortedNodes


class SortedNodesToParallelizedStages:
    def calculate(self, sorted_nodes: SortedNodes) -> ParallelStagesList:
        parallelized = [
            ParallelStages({node.content for node in nodes.nodes})
            for nodes in sorted_nodes.all
        ]
        return ParallelStagesList(parallelized)
