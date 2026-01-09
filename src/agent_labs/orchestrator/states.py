"""
Agent state definitions and transition logic.
"""

from enum import Enum
from typing import Dict, Set


class AgentState(Enum):
    """Agent execution states in the orchestration loop."""

    OBSERVING = "observing"  # Reading input/goal
    PLANNING = "planning"  # Using LLM to decide next action
    ACTING = "acting"  # Executing the planned action
    VERIFYING = "verifying"  # Checking if result achieves goal
    REFINING = "refining"  # Learning from result for next iteration
    DONE = "done"  # Task complete
    FAILED = "failed"  # Task failed


# Valid state transitions
STATE_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.OBSERVING: {AgentState.PLANNING, AgentState.FAILED},
    AgentState.PLANNING: {AgentState.ACTING, AgentState.FAILED},
    AgentState.ACTING: {AgentState.VERIFYING, AgentState.FAILED},
    AgentState.VERIFYING: {AgentState.DONE, AgentState.REFINING, AgentState.FAILED},
    AgentState.REFINING: {AgentState.OBSERVING, AgentState.FAILED},
    AgentState.DONE: set(),  # Terminal state
    AgentState.FAILED: set(),  # Terminal state
}


def can_transition(from_state: AgentState, to_state: AgentState) -> bool:
    """
    Check if transition from one state to another is valid.
    
    Args:
        from_state: Current state
        to_state: Target state
        
    Returns:
        True if transition is valid, False otherwise
    """
    return to_state in STATE_TRANSITIONS.get(from_state, set())


def get_valid_transitions(state: AgentState) -> Set[AgentState]:
    """
    Get all valid transitions from a given state.
    
    Args:
        state: Current state
        
    Returns:
        Set of valid next states
    """
    return STATE_TRANSITIONS.get(state, set())
