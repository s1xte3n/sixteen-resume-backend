from typing import Protocol


class VisitorCounter(Protocol):
    def increment(self) -> int:
        """Atomically increment and return the committed count."""
