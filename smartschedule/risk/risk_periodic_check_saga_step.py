from enum import StrEnum, auto


class RiskPeriodicCheckSagaStep(StrEnum):
    FIND_AVAILABLE = auto()
    DO_NOTHING = auto()
    SUGGEST_REPLACEMENT = auto()
    NOTIFY_ABOUT_POSSIBLE_RISK = auto()
    NOTIFY_ABOUT_DEMANDS_SATISFIED = auto()
