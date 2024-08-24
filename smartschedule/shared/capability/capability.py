from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    name: str
    type: str

    @classmethod
    def skill(cls, name: str) -> Capability:
        return Capability(name, "SKILL")

    @classmethod
    def skills(cls, *names: str) -> set[Capability]:
        return {Capability(name, "SKILL") for name in names}

    @classmethod
    def permission(cls, name: str) -> Capability:
        return Capability(name, "PERMISSION")

    @classmethod
    def permissions(cls, *names: str) -> set[Capability]:
        return {Capability(name, "PERMISSION") for name in names}

    @classmethod
    def asset(cls, asset: str) -> Capability:
        return Capability(asset, "ASSET")

    @classmethod
    def assets(cls, *assets: str) -> set[Capability]:
        return {Capability(asset, "ASSET") for asset in assets}

    def is_of_type(self, type: str) -> bool:
        return self.type == type
