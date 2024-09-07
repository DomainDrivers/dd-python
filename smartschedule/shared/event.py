from datetime import datetime
from typing import Protocol


class Event(Protocol):
    @property
    def occurred_at(self) -> datetime: ...
