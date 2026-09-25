class VisitorCounterDependencyError(Exception):
    """Raised when the visitor-counter persistence dependency cannot complete an operation."""


class VisitorCounterTimeoutError(VisitorCounterDependencyError):
    """Raised when the persistence dependency times out."""
