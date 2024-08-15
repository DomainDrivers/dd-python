from __future__ import annotations
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TypeAlias


@dataclass
class Stage:
    name: str
    dependencies: set[Stage] = field(default_factory=set, compare=False)
    resources: set[ResourceName] = field(default_factory=set, compare=False)
    duration: timedelta = field(default_factory=timedelta, compare=False)

    def depends_on(self, stage: Stage) -> Stage:
        new_dependencies = self.dependencies.union({stage})
        self.dependencies.add(stage)
        return Stage(self.name, new_dependencies, self.resources, self.duration)

    def with_chosen_resource_capabilities(self, *resources: ResourceName) -> Stage:
        return Stage(self.name, self.dependencies, set(resources), self.duration)

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


ResourceName: TypeAlias = str
