from dataclasses import dataclass, field
from uuid import UUID, uuid4

from smartschedule.optimization.capacity_dimension import CapacityDimension
from smartschedule.optimization.weight_dimension import WeightDimension
from smartschedule.shared.timeslot.time_slot import TimeSlot


@dataclass(frozen=True)
class CapabilityCapacityDimension(CapacityDimension):
    uuid: UUID = field(default_factory=uuid4, init=False)
    id: str
    capacity_name: str
    capacity_type: str


@dataclass(frozen=True)
class CapabilityWeightDimension(WeightDimension[CapabilityCapacityDimension]):
    name: str
    type: str

    def is_satisfied_by(self, capacity: CapabilityCapacityDimension) -> bool:
        return (
            capacity.capacity_name == self.name and capacity.capacity_type == self.type
        )


@dataclass(frozen=True)
class CapabilityTimedCapacityDimension(CapacityDimension):
    uuid: UUID = field(default_factory=uuid4, init=False)
    id: str
    capacity_name: str
    capacity_type: str
    time_slot: TimeSlot


@dataclass(frozen=True)
class CapabilityTimedWeightDimension(WeightDimension[CapabilityTimedCapacityDimension]):
    name: str
    type: str
    time_slot: TimeSlot

    def is_satisfied_by(self, capacity: CapabilityTimedCapacityDimension) -> bool:
        return (
            capacity.capacity_name == self.name
            and capacity.capacity_type == self.type
            and self.time_slot.within(capacity.time_slot)
        )
