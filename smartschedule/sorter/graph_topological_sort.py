from itertools import chain
from smartschedule.sorter.nodes import Nodes
from smartschedule.sorter.sorted_nodes import SortedNodes


def graph_topological_sort[T](nodes: Nodes[T]) -> SortedNodes[T]:
    return _create_sorted_nodes_recursively(nodes, SortedNodes[T].empty())


def _create_sorted_nodes_recursively[T](
    remaining_nodes: Nodes[T], accumulated_sorted_nodes: SortedNodes[T]
) -> SortedNodes[T]:
    accumulated_nodes = [nodes.nodes for nodes in accumulated_sorted_nodes.all]
    already_processed_nodes = list(chain.from_iterable(accumulated_nodes))

    nodes_without_dependencies = remaining_nodes.with_all_dependencies_present_in(
        already_processed_nodes
    )

    if not nodes_without_dependencies.all:
        return accumulated_sorted_nodes

    new_sorted_nodes = accumulated_sorted_nodes.add(nodes_without_dependencies)
    remaining_nodes = remaining_nodes.remove_all(nodes_without_dependencies.all)
    return _create_sorted_nodes_recursively(remaining_nodes, new_sorted_nodes)
