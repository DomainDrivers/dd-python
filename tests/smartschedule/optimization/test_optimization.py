from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.optimization.item import Item
from smartschedule.optimization.optimization_facade import OptimizationFacade
from smartschedule.optimization.total_capacity import TotalCapacity
from smartschedule.optimization.total_weight import TotalWeight
from tests.smartschedule.optimization.capability_capacity_dimension import (
    CapabilityCapacityDimension,
    CapabilityWeightDimension,
)


class TestOptimization:
    def test_nothing_is_chosen_when_no_capacities(
        self, optimization_facade: OptimizationFacade
    ) -> None:
        items = [
            Item(
                "Item1",
                100,
                TotalWeight.of(CapabilityWeightDimension("COMMON SENSE", "Skill")),
            ),
            Item(
                "Item2",
                100,
                TotalWeight.of(CapabilityWeightDimension("THINKING", "Skill")),
            ),
        ]

        result = optimization_facade.calculate(items, TotalCapacity.zero())

        assert result.profit == 0
        assert len(result.chosen_items) == 0

    def test_everything_is_chosen_when_all_weights_are_zero(
        self, optimization_facade: OptimizationFacade
    ) -> None:
        items: list[Item[CapacityDimension]] = [
            Item("Item1", 200, TotalWeight.zero()),
            Item("Item2", 100, TotalWeight.zero()),
        ]

        result = optimization_facade.calculate(items, TotalCapacity.zero())

        assert result.profit == 300
        assert len(result.chosen_items) == 2

    def test_if_enough_capacity_all_items_are_chosen(
        self, optimization_facade: OptimizationFacade
    ) -> None:
        items = [
            Item(
                "Item1",
                100,
                TotalWeight.of(CapabilityWeightDimension("WEB DEVELOPMENT", "Skill")),
            ),
            Item(
                "Item2",
                300,
                TotalWeight.of(CapabilityWeightDimension("WEB DEVELOPMENT", "Skill")),
            ),
        ]
        c1 = CapabilityCapacityDimension("anna", "WEB DEVELOPMENT", "Skill")
        c2 = CapabilityCapacityDimension("zbyniu", "WEB DEVELOPMENT", "Skill")

        result = optimization_facade.calculate(items, TotalCapacity.of(c1, c2))

        assert result.profit == 400
        assert len(result.chosen_items) == 2

    def test_most_valuable_items_are_chosen(
        self, optimization_facade: OptimizationFacade
    ) -> None:
        item1 = Item(
            "Item1", 100, TotalWeight.of(CapabilityWeightDimension("JAVA", "Skill"))
        )
        item2 = Item(
            "Item2", 500, TotalWeight.of(CapabilityWeightDimension("JAVA", "Skill"))
        )
        item3 = Item(
            "Item3", 300, TotalWeight.of(CapabilityWeightDimension("JAVA", "Skill"))
        )
        c1 = CapabilityCapacityDimension("anna", "JAVA", "Skill")
        c2 = CapabilityCapacityDimension("zbyniu", "JAVA", "Skill")

        result = optimization_facade.calculate(
            [item1, item2, item3], TotalCapacity.of(c1, c2)
        )

        assert result.profit == 800
        assert len(result.chosen_items) == 2
        assert result.item_to_capacities[item3] == {c1} or {c2}
        assert result.item_to_capacities[item2] == {c1} or {c2}
        assert item1 not in result.item_to_capacities
