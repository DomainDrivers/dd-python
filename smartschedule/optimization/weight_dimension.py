import abc

from smartschedule.optimization.capacity_dimension import CapacityDimension


class WeightDimension[T: CapacityDimension](abc.ABC):
    @abc.abstractmethod
    def is_satisfied_by(self, capacity: T) -> bool:
        pass
