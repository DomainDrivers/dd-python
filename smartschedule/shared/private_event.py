import inspect
from dataclasses import dataclass, is_dataclass
from datetime import datetime


# metadata:
#  - correlation_id
#  - potential aggregate's id
#  - causation_id - id of a message that caused this message
#  - message_id - unique id of the message
#  - user - if there is any (might be a system event)
@dataclass(frozen=True)
class PrivateEvent:
    def __init_subclass__(cls) -> None:
        if not is_dataclass(cls):
            raise TypeError("PrivateEvent subclasses must be dataclasses")
        annotations = inspect.get_annotations(cls)
        if "occurred_at" not in annotations or annotations["occurred_at"] != datetime:
            raise TypeError(
                "PrivateEvent subclasses must have an occurred_at field of type datetime"
            )
        return super().__init_subclass__()
