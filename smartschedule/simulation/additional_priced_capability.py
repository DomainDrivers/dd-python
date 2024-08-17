from dataclasses import dataclass
from decimal import Decimal

from smartschedule.simulation.available_resource_capability import (
    AvailableResourceCapability,
)


@dataclass(frozen=True)
class AdditionalPricedCapability:
    value: Decimal
    available_resource_capability: AvailableResourceCapability
