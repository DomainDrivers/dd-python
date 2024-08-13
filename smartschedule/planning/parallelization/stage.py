from __future__ import annotations
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TypeAlias


@dataclass
class Stage:
    name: str
    dependencies: set[Stage] = field(default_factory=set, init=False, compare=False)
    resources: set[ResourceName] = field(default_factory=set, init=False, compare=False)
    duration: timedelta = field(default_factory=timedelta, init=False, compare=False)

    def depends_on(self, stage: Stage) -> Stage:
        self.dependencies.add(stage)
        return self

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)


ResourceName: TypeAlias = str
