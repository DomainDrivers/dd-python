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
    def permission(cls, name: str) -> Capability:
        return Capability(name, "PERMISSION")

    @classmethod
    def asset(cls, asset: str) -> Capability:
        return Capability(asset, "ASSET")
