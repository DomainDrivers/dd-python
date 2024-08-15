from smartschedule.planning.parallelization.stage import Stage
from smartschedule.sorter.feedback_arc_se_on_graph import Edge, FeedbackArcSeOnGraph
from smartschedule.sorter.node import Node


class TestFeedbackArcSeOnGraph:
    def test_can_find_minimum_number_of_edges_to_remove_to_make_the_graph_acyclic(
        self,
    ) -> None:
        node1 = Node("1", Stage("1"))
        node2 = Node("2", Stage("2"))
        node3 = Node("3", Stage("3"))
        node4 = Node("4", Stage("4"))
        node1 = node1.depends_on(node2)
        node2 = node2.depends_on(node3)
        node4 = node4.depends_on(node3)
        node1 = node1.depends_on(node4)
        node3 = node3.depends_on(node1)

        to_remove = FeedbackArcSeOnGraph.calculate([node1, node2, node3, node4])

        assert to_remove == [Edge(3, 1), Edge(4, 3)]

    def test_when_graph_is_acyclic_there_is_nothing_to_remove(self) -> None:
        node1 = Node("1", Stage("1"))
        node2 = Node("2", Stage("2"))
        node3 = Node("3", Stage("3"))
        node4 = Node("4", Stage("4"))
        node1 = node1.depends_on(node2)
        node2 = node2.depends_on(node3)
        node1 = node1.depends_on(node4)

        to_remove = FeedbackArcSeOnGraph.calculate([node1, node2, node3, node4])

        assert to_remove == []
