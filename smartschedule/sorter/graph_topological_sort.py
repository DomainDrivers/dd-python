from itertools import chain
from smartschedule.sorter.nodes import Nodes
from smartschedule.sorter.sorted_nodes import SortedNodes


class GraphTopologicalSort:
    def sort(self, nodes: Nodes) -> SortedNodes:
        return self._create_sorted_nodes_recursively(nodes, SortedNodes.empty())

    def _create_sorted_nodes_recursively(
        self, remaining_nodes: Nodes, accumulated_sorted_nodes: SortedNodes
    ) -> SortedNodes:
        accumulated_nodes = [nodes.nodes for nodes in accumulated_sorted_nodes.all]
        already_processed_nodes = list(chain.from_iterable(accumulated_nodes))

        nodes_without_dependencies = remaining_nodes.with_all_dependencies_present_in(
            already_processed_nodes
        )

        if not nodes_without_dependencies.all:
            return accumulated_sorted_nodes

        new_sorted_nodes = accumulated_sorted_nodes.add(nodes_without_dependencies)
        remaining_nodes = remaining_nodes.remove_all(nodes_without_dependencies.all)
        return self._create_sorted_nodes_recursively(remaining_nodes, new_sorted_nodes)
