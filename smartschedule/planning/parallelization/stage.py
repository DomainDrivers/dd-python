from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from smartschedule.availability.resource_id import ResourceId


@dataclass()
class Stage:
    name: str
    dependencies: set[Stage] = field(default_factory=set)
    resources: frozenset[ResourceId] = field(default_factory=frozenset)
    duration: timedelta = field(default_factory=timedelta)

    def depends_on(self, stage: Stage) -> Stage:
        new_dependencies = self.dependencies.union({stage})
        self.dependencies = new_dependencies
        return Stage(self.name, new_dependencies, self.resources, self.duration)

    def with_chosen_resource_capabilities(self, *resources: ResourceId) -> Stage:
        return Stage(self.name, self.dependencies, frozenset(resources), self.duration)

    def of_duration(self, duration: timedelta) -> Stage:
        return Stage(self.name, self.dependencies, self.resources, duration)

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)
