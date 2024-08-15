import pytest

from smartschedule.sorter.graph_topological_sort import GraphTopologicalSort
from smartschedule.sorter.node import Node
from smartschedule.sorter.nodes import Nodes


@pytest.fixture
def graph_topological_sort() -> GraphTopologicalSort[str]:
    return GraphTopologicalSort[str]()


class TestGraphTopologicalSort:
    def test_topological_sort_with_simple_dependencies(
        self, graph_topological_sort: GraphTopologicalSort[str]
    ) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        node3 = Node("Node3", "node3")
        node4 = Node("Node4", "node4")
        node2 = node2.depends_on(node1)
        node3 = node3.depends_on(node1)
        node4 = node4.depends_on(node2)

        nodes = Nodes[str]({node1, node2, node3, node4})

        sorted_nodes = graph_topological_sort.sort(nodes)

        assert len(sorted_nodes.all) == 3

        assert len(sorted_nodes.all[0].nodes) == 1
        assert node1 in sorted_nodes.all[0].nodes

        assert len(sorted_nodes.all[1].nodes) == 2
        assert node2 in sorted_nodes.all[1].nodes
        assert node3 in sorted_nodes.all[1].nodes

        assert len(sorted_nodes.all[2].nodes) == 1
        assert node4 in sorted_nodes.all[2].nodes

    def test_topological_sort_with_linear_dependencies(
        self, graph_topological_sort: GraphTopologicalSort[str]
    ) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        node3 = Node("Node3", "node3")
        node4 = Node("Node4", "node4")
        node5 = Node("Node5", "node5")
        node1 = node1.depends_on(node2)
        node2 = node2.depends_on(node3)
        node3 = node3.depends_on(node4)
        node4 = node4.depends_on(node5)

        nodes = Nodes({node1, node2, node3, node4, node5})

        sorted_nodes = graph_topological_sort.sort(nodes)

        assert len(sorted_nodes.all) == 5

        assert len(sorted_nodes.all[0].nodes) == 1
        assert node5 in sorted_nodes.all[0].nodes

        assert len(sorted_nodes.all[1].nodes) == 1
        assert node4 in sorted_nodes.all[1].nodes

        assert len(sorted_nodes.all[2].nodes) == 1
        assert node3 in sorted_nodes.all[2].nodes

        assert len(sorted_nodes.all[3].nodes) == 1
        assert node2 in sorted_nodes.all[3].nodes

        assert len(sorted_nodes.all[4].nodes) == 1
        assert node1 in sorted_nodes.all[4].nodes

    def test_nodes_without_dependencies(
        self, graph_topological_sort: GraphTopologicalSort[str]
    ) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        nodes = Nodes({node1, node2})

        sorted_nodes = graph_topological_sort.sort(nodes)

        assert len(sorted_nodes.all) == 1

    def test_cyclic_dependency(
        self, graph_topological_sort: GraphTopologicalSort[str]
    ) -> None:
        node1 = Node("Node1", "node1")
        node2 = Node("Node2", "node2")
        node2 = node2.depends_on(node1)
        node1 = node1.depends_on(node2)
        nodes = Nodes({node1, node2})

        sorted_nodes = graph_topological_sort.sort(nodes)

        assert len(sorted_nodes.all) == 0
