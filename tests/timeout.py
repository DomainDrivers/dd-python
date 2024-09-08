import time
from typing import Callable


def timeout(milliseconds: int, callable: Callable[[], None]) -> None:
    start = time.monotonic()
    end = start + milliseconds / 1000
    while time.monotonic() <= end:
        try:
            callable()
        except AssertionError:
            time.sleep(0.05)
        else:
            return

    raise TimeoutError("Timeout reached")


def timeout_never(milliseconds: int, callable: Callable[[], None]) -> None:
    __tracebackhide__ = True

    start = time.monotonic()
    end = start + milliseconds / 1000
    while time.monotonic() <= end:
        try:
            callable()
        except AssertionError:
            time.sleep(0.05)
        else:
            raise AssertionError("Condition should never be met")
