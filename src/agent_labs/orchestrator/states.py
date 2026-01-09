"""Agent orchestration states and transitions."""

from enum import Enum
from typing import Dict, Iterable, Set


class AgentState(Enum):
    """Agent execution states in the orchestration loop."""

    OBSERVING = "observing"
    PLANNING = "planning"
    ACTING = "acting"
    VERIFYING = "verifying"
    REFINING = "refining"
    DONE = "done"
    FAILED = "failed"


_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.OBSERVING: {AgentState.PLANNING},
    AgentState.PLANNING: {AgentState.ACTING},
    AgentState.ACTING: {AgentState.VERIFYING},
    AgentState.VERIFYING: {AgentState.DONE, AgentState.REFINING},
    AgentState.REFINING: {AgentState.OBSERVING},
    AgentState.DONE: set(),
    AgentState.FAILED: set(),
}


def can_transition(current: AgentState, target: AgentState) -> bool:
    """Check if the state transition is valid."""
    if target == AgentState.FAILED:
        return True
    return target in _TRANSITIONS.get(current, set())


def get_valid_transitions(state: AgentState) -> Iterable[AgentState]:
    """Return valid transitions for a given state."""
    return _TRANSITIONS.get(state, set())
