"""Orchestrator-specific exceptions."""


class OrchestratorError(Exception):
    """Base exception for agent orchestration errors."""


class MaxTurnsExceededError(OrchestratorError):
    """Raised when the agent exceeds max_turns without completion."""


class VerificationError(OrchestratorError):
    """Raised when verification fails unexpectedly."""


class PlanningError(OrchestratorError):
    """Raised when planning fails."""


class ActionExecutionError(OrchestratorError):
    """Raised when action execution fails."""


class StateTransitionError(OrchestratorError):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(f"Invalid state transition: {from_state} -> {to_state}")
