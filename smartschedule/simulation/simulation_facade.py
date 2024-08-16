from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)
from smartschedule.simulation.demands import Demands
from smartschedule.simulation.result import Result
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities
from smartschedule.simulation.simulated_project import SimulatedProject


class SimulationFacade:
    def which_project_with_missing_demands_is_most_profitable_to_allocate_resources_to(
        self,
        projects_simulations: list[SimulatedProject],
        total_capability: SimulatedCapabilities,
    ) -> Result:
        capabilities = total_capability.capabilities
        capacities_size = len(capabilities)
        dp = [0] * (capacities_size + 1)
        chosen_items_list: list[list[SimulatedProject]] = [
            [] for _ in range(capacities_size + 1)
        ]
        allocated_capacities_list: list[set[AvailableResourceCapability]] = [
            set() for _ in range(capacities_size + 1)
        ]

        automatically_included_items = [
            project
            for project in projects_simulations
            if project.all_demands_satisfied()
        ]
        guaranteed_value = sum(
            [project.earnings for project in automatically_included_items]
        )

        all_availabilities = capabilities.copy()
        item_to_capacities_map: dict[
            SimulatedProject, set[AvailableResourceCapability]
        ] = {}

        for project in sorted(
            projects_simulations, key=lambda x: x.earnings, reverse=True
        ):
            chosen_capacities = self._match_capacities(
                project.missing_demands, all_availabilities
            )
            all_availabilities = [
                x for x in all_availabilities if x not in chosen_capacities
            ]

            if not chosen_capacities:
                continue

            sum_value = int(project.earnings)
            chosen_capacities_count = len(chosen_capacities)

            for j in range(capacities_size, chosen_capacities_count - 1, -1):
                if dp[j] < sum_value + dp[j - chosen_capacities_count]:
                    dp[j] = sum_value + dp[j - chosen_capacities_count]

                    chosen_items_list[j] = chosen_items_list[
                        j - chosen_capacities_count
                    ].copy()
                    chosen_items_list[j].append(project)

                    allocated_capacities_list[j].update(chosen_capacities)

            item_to_capacities_map[project] = set(chosen_capacities)

        chosen_items_list[capacities_size].extend(automatically_included_items)
        return Result(
            float(dp[capacities_size] + guaranteed_value),
            chosen_items_list[capacities_size],
            item_to_capacities_map,
        )

    def _match_capacities(
        self, demands: Demands, available_capacities: list[AvailableResourceCapability]
    ) -> list[AvailableResourceCapability]:
        result = []
        for single_demand in demands.all:
            matching_capacity = next(
                (x for x in available_capacities if single_demand.is_satisfied_by(x)),
                None,
            )

            if matching_capacity:
                result.append(matching_capacity)
            else:
                return []
        return result
