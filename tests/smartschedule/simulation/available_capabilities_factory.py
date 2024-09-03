from __future__ import annotations

import factory  # type: ignore

from smartschedule.shared.capability.capability import Capability
from smartschedule.shared.capability_selector import CapabilitySelector, SelectingPolicy
from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)
from smartschedule.simulation.simulated_capabilities import SimulatedCapabilities


class SimulatedCapabilitiesFactory(factory.Factory):  # type: ignore
    class Meta:
        model = SimulatedCapabilities

    class Params:
        num_capabilities = 0

    @factory.lazy_attribute  # type: ignore
    def capabilities(self) -> list[AvailableResourceCapability]:
        result = []
        argument_src = self._Resolver__declarations["capabilities"].context
        for index in range(self.num_capabilities):
            brings = argument_src[f"{index}__brings"]
            if isinstance(brings, Capability):
                capabilities = frozenset([brings])
                selecting_policy = SelectingPolicy.ONE_OF_ALL
            elif isinstance(brings, set):
                if not all(isinstance(x, Capability) for x in brings):
                    raise ValueError(
                        "All elements of the set must be of type Capability"
                    )
                capabilities = frozenset(brings)
                selecting_policy = SelectingPolicy.ALL_SIMULTANEOUSLY

            capability = AvailableResourceCapability(
                resource_id=argument_src[f"{index}__resource_id"],
                capability_selector=CapabilitySelector(
                    capabilities=capabilities, selecting_policy=selecting_policy
                ),
                time_slot=argument_src[f"{index}__time_slot"],
            )
            result.append(capability)
        return result
