from __future__ import annotations

from dataclasses import dataclass

from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.sorted_nodes_to_parallelized_stages import (
    SortedNodesToParallelizedStages,
)
from smartschedule.planning.parallelization.stage import Stage
from smartschedule.planning.parallelization.stages_to_nodes import StagesToNodes
from smartschedule.sorter.edge import Edge
from smartschedule.sorter.feedback_arc_se_on_graph import FeedbackArcSeOnGraph
from smartschedule.sorter.graph_topological_sort import GraphTopologicalSort


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        nodes = StagesToNodes().calculate(list(stages))
        sorted_nodes = GraphTopologicalSort[Stage]().sort(nodes)
        return SortedNodesToParallelizedStages().calculate(sorted_nodes)

    def what_to_remove(self, stages: set[Stage]) -> RemovalSuggestion:
        nodes = StagesToNodes().calculate(list(stages))
        result = FeedbackArcSeOnGraph[Stage]().calculate(list(nodes.nodes))
        return RemovalSuggestion(result)


@dataclass(frozen=True)
class RemovalSuggestion:
    edges: list[Edge]

    def __str__(self) -> str:
        return f"[{', '.join(str(edge) for edge in self.edges)}]"
