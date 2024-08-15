from smartschedule.planning.parallelization.stage import Stage
from smartschedule.sorter.node import Node
from smartschedule.sorter.nodes import Nodes


def stages_to_nodes(stages: list[Stage]) -> Nodes[Stage]:
    result: dict[str, Node[Stage]] = {
        stage.name: Node(stage.name, stage) for stage in stages
    }

    for i, stage in enumerate(stages):
        _explicit_dependencies(stage, result)
        _shared_resources(stage, stages[i + 1 :], result)

    return Nodes(set(result.values()))


def _shared_resources(
    stage: Stage, with_stages: list[Stage], result: dict[str, Node[Stage]]
) -> None:
    for other in with_stages:
        if stage.name != other.name:
            if not stage.resources.isdisjoint(other.resources):
                if len(other.resources) > len(stage.resources):
                    node = result[stage.name].depends_on(result[other.name])
                    result[stage.name] = node
                else:
                    node = result[other.name].depends_on(result[stage.name])
                    result[other.name] = node


def _explicit_dependencies(stage: Stage, result: dict[str, Node[Stage]]) -> None:
    node_with_explicit_deps = result[stage.name]
    for explicit_dependency in stage.dependencies:
        node_with_explicit_deps = node_with_explicit_deps.depends_on(
            result[explicit_dependency.name]
        )
    result[stage.name] = node_with_explicit_deps
