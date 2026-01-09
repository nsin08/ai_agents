"""
Agent context data structure.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Any, Callable

from .states import AgentState


@dataclass
class AgentContext:
    """
    Context and state for an agent execution run.
    
    This class holds all the information needed for an agent's execution,
    including the goal, conversation history, current state, and metadata.
    """

    goal: str
    """What the agent is trying to accomplish."""

    inputs: dict = field(default_factory=dict)
    """Optional inputs/parameters for the agent."""

    turn_count: int = 0
    """How many iterations (turns) the agent has taken."""

    history: List[Tuple[str, str]] = field(default_factory=list)
    """Conversation history: list of (role, message) tuples."""

    current_state: AgentState = AgentState.OBSERVING
    """Current state in the agent loop."""

    metadata: dict = field(default_factory=dict)
    """Additional metadata (costs, tokens, latency, etc.)."""

    memory_refs: List[str] = field(default_factory=list)
    """References to memory/context retrieved during execution."""

    def add_history(self, role: str, message: str) -> None:
        """
        Add an entry to conversation history.
        
        Args:
            role: Role of the speaker (user, assistant, system, tool)
            message: The message content
        """
        self.history.append((role, message))

    def get_recent_history(self, n: int = 3) -> List[Tuple[str, str]]:
        """
        Get the most recent n entries from history.
        
        Args:
            n: Number of recent entries to retrieve
            
        Returns:
            List of recent (role, message) tuples
        """
        return self.history[-n:]

    def format_history(self, n: Optional[int] = None) -> str:
        """
        Format history as a string for prompts.
        
        Args:
            n: Number of recent entries to include (None = all)
            
        Returns:
            Formatted history string
        """
        entries = self.history if n is None else self.history[-n:]
        return "\n".join([f"{role}: {msg}" for role, msg in entries])

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata entry.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)


@dataclass
class VerificationResult:
    """Result of verification step."""
    
    is_complete: bool
    """Whether the goal is achieved."""
    
    confidence: float = 1.0
    """Confidence score (0.0 to 1.0)."""
    
    reason: str = ""
    """Explanation of why verification passed/failed."""
    
    feedback: str = ""
    """Feedback for refinement if verification failed."""
