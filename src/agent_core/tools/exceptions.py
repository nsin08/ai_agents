"""Tool execution error types."""

from __future__ import annotations


class ToolExecutionError(RuntimeError):
    """Base class for tool execution errors."""

    error_type = "ToolError"

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class ToolNotFound(ToolExecutionError):
    error_type = "ToolNotFound"


class ToolTimeout(ToolExecutionError):
    error_type = "ToolTimeout"


class ToolProviderError(ToolExecutionError):
    error_type = "ToolProviderError"


class ToolResultInvalid(ToolExecutionError):
    error_type = "ToolResultInvalid"


class ToolInputInvalid(ToolExecutionError):
    error_type = "ToolInputInvalid"


class PolicyViolation(ToolExecutionError):
    error_type = "PolicyViolation"


class BudgetExceeded(ToolExecutionError):
    error_type = "BudgetExceeded"


__all__ = [
    "BudgetExceeded",
    "PolicyViolation",
    "ToolExecutionError",
    "ToolInputInvalid",
    "ToolNotFound",
    "ToolProviderError",
    "ToolResultInvalid",
    "ToolTimeout",
]
