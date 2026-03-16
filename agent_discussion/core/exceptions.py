"""Custom exception classes for Agent Discussion."""


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""


class WorkflowStateError(Exception):
    """Raised when an invalid workflow state transition is attempted."""
