from itertools import chain

from smartschedule.planning.parallelization.parallel_stages import ParallelStages
from smartschedule.planning.parallelization.parallel_stages_list import (
    ParallelStagesList,
)
from smartschedule.planning.parallelization.stage import Stage


class StageParallelization:
    def of(self, stages: set[Stage]) -> ParallelStagesList:
        return self._create_sorted_notes_recursively(stages, ParallelStagesList.empty())

    def _create_sorted_notes_recursively(
        self, remaining_nodes: set[Stage], accumulated_sorted_nodes: ParallelStagesList
    ) -> ParallelStagesList:
        accumulated_stages = [
            parallel_stages.stages for parallel_stages in accumulated_sorted_nodes.all
        ]
        already_processed_nodes: set[Stage] = set(
            chain.from_iterable(accumulated_stages)
        )
        nodes_without_dependencies = {
            node
            for node in remaining_nodes
            if not node.dependencies - already_processed_nodes
        }

        if not nodes_without_dependencies:
            return accumulated_sorted_nodes

        new_sorted_nodes = accumulated_sorted_nodes.add(
            ParallelStages(stages=nodes_without_dependencies)
        )
        new_remaining_nodes = remaining_nodes.difference(nodes_without_dependencies)
        return self._create_sorted_notes_recursively(
            new_remaining_nodes, new_sorted_nodes
        )
