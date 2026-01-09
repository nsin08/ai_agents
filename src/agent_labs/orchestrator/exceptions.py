"""
Custom exceptions for orchestrator module.
"""


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass


class MaxTurnsExceededError(OrchestratorError):
    """Raised when agent exceeds maximum allowed turns without completing goal."""
    
    def __init__(self, turns: int, goal: str):
        self.turns = turns
        self.goal = goal
        super().__init__(f"Max turns ({turns}) exceeded without completing goal: {goal}")


class VerificationError(OrchestratorError):
    """Raised when verification step fails."""
    
    def __init__(self, message: str, result: str):
        self.result = result
        super().__init__(f"Verification failed: {message}")


class PlanningError(OrchestratorError):
    """Raised when planning step fails."""
    
    def __init__(self, message: str, context: str):
        self.context = context
        super().__init__(f"Planning failed: {message}")


class ActionExecutionError(OrchestratorError):
    """Raised when action execution fails."""
    
    def __init__(self, message: str, plan: str):
        self.plan = plan
        super().__init__(f"Action execution failed: {message}")


class StateTransitionError(OrchestratorError):
    """Raised when invalid state transition is attempted."""
    
    def __init__(self, from_state: str, to_state: str):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"Invalid state transition: {from_state} -> {to_state}")
