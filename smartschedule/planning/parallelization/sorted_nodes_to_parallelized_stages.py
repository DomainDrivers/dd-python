from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.sorter.sorted_nodes import SortedNodes


def sorted_nodes_to_parallelized_stages(
    sorted_nodes: SortedNodes[Stage],
) -> ParallelStagesList:
    return ParallelStagesList(
        [
            ParallelStages({node.content for node in nodes.nodes})
            for nodes in sorted_nodes.all
        ]
    )
