"""Agent context and verification structures."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .states import AgentState


@dataclass
class VerificationResult:
    """Result of verifying if the goal is complete."""

    is_complete: bool
    confidence: float = 1.0
    reason: str = ""
    feedback: str = ""


@dataclass
class AgentContext:
    """Context and state for an agent execution run."""

    goal: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    turn_count: int = 0
    history: List[Tuple[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    current_state: AgentState = AgentState.OBSERVING

    def add_history(self, role: str, message: str) -> None:
        """Append a message to the conversation history."""
        self.history.append((role, message))

    def get_recent_history(self, n: int = 5) -> List[Tuple[str, str]]:
        """Return the most recent n history items."""
        if n <= 0:
            return []
        return self.history[-n:]

    def format_history(self, n: int = 5) -> str:
        """Format recent history for prompts."""
        recent = self.get_recent_history(n=n)
        return "\n".join(f"{role}: {message}" for role, message in recent)

    def add_metadata(self, key: str, value: Any) -> None:
        """Store arbitrary metadata in context."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve metadata value by key."""
        return self.metadata.get(key, default)
