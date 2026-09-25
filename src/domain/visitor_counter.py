from threading import Lock


class InMemoryVisitorCounter:
    """Thread-safe in-memory counter used by deterministic local unit tests."""

    def __init__(self, initial_count: int = 0):
        if initial_count < 0:
            raise ValueError("initial_count must be non-negative")
        self._count = initial_count
        self._lock = Lock()

    def increment(self) -> int:
        with self._lock:
            self._count += 1
            return self._count

    @property
    def count(self) -> int:
        with self._lock:
            return self._count
