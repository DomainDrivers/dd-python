from __future__ import annotations

from dataclasses import dataclass

from smartschedule.availability.owner import Owner


@dataclass(frozen=True)
class Blockade:
    taken_by: Owner
    disabled: bool

    @staticmethod
    def none() -> Blockade:
        return Blockade(Owner.none(), False)

    @staticmethod
    def disabled_by(owner: Owner) -> Blockade:
        return Blockade(owner, True)

    @staticmethod
    def owned_by(owner: Owner) -> Blockade:
        return Blockade(owner, False)

    def can_be_taken_by(self, requester: Owner) -> bool:
        return self.taken_by == Owner.none() or self.taken_by == requester

    def is_disabled_by(self, owner: Owner) -> bool:
        return self.disabled and self.taken_by == owner
