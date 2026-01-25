"""
Session-based memory for conversational agents.

Provides SessionStore interface and InMemorySessionStore implementation
for managing conversation context with thread-safety and token counting.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class SessionStore(ABC):
    """Abstract interface for session-based conversation memory."""

    @abstractmethod
    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to the session.

        Args:
            role: Message role ("user", "assistant", or "system")
            content: Message content
            metadata: Optional metadata dictionary
        """
        raise NotImplementedError

    @abstractmethod
    def get_context(self, format: str = "list") -> Any:
        """Get conversation context.

        Args:
            format: Output format ("list" for list of dicts, "string" for formatted text)

        Returns:
            Conversation history in requested format
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Clear all messages from the session."""
        raise NotImplementedError

    @abstractmethod
    def get_token_count(self) -> int:
        """Get approximate token count for current context.

        Returns:
            Approximate number of tokens
        """
        raise NotImplementedError


class InMemorySessionStore(SessionStore):
    """Thread-safe in-memory session store for conversation management.

    Features:
    - Thread-safe operations using threading.Lock
    - Automatic truncation when max_turns exceeded
    - Token counting (approximate, using character-based heuristic)
    - Support for user, assistant, and system messages
    """

    def __init__(self, max_turns: int = 20) -> None:
        """Initialize session store.

        Args:
            max_turns: Maximum number of turns (message pairs) to keep

        Raises:
            ValueError: If max_turns is not positive
        """
        if max_turns <= 0:
            raise ValueError("max_turns must be positive")

        self._max_turns = max_turns
        self._messages: List[Message] = []
        self._lock = threading.Lock()

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to the session (thread-safe).

        Args:
            role: Message role ("user", "assistant", or "system")
            content: Message content
            metadata: Optional metadata dictionary

        Raises:
            ValueError: If role is not valid
        """
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'")

        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        with self._lock:
            self._messages.append(message)
            self._enforce_max_turns()

    def _enforce_max_turns(self) -> None:
        """Enforce max_turns limit by removing oldest messages.

        System messages are preserved. Only user/assistant pairs are counted as turns.
        """
        # Count non-system messages (user/assistant exchanges)
        non_system_count = sum(1 for msg in self._messages if msg.role != "system")

        # If we exceed max_turns * 2 (each turn has user + assistant), remove oldest
        max_messages = self._max_turns * 2
        if non_system_count > max_messages:
            # Build new list preserving system messages and newest messages
            system_messages = [msg for msg in self._messages if msg.role == "system"]
            non_system_messages = [msg for msg in self._messages if msg.role != "system"]

            # Keep only the newest messages
            kept_non_system = non_system_messages[-max_messages:]

            # Rebuild messages list with system messages first, then conversation
            self._messages = system_messages + kept_non_system

    def get_context(self, format: str = "list") -> Any:
        """Get conversation context (thread-safe).

        Args:
            format: Output format ("list" for list of dicts, "string" for formatted text)

        Returns:
            Conversation history in requested format

        Raises:
            ValueError: If format is not valid
        """
        if format not in ("list", "string"):
            raise ValueError(f"Invalid format: {format}. Must be 'list' or 'string'")

        with self._lock:
            messages_copy = list(self._messages)

        if format == "list":
            return [msg.to_dict() for msg in messages_copy]
        else:  # format == "string"
            lines = []
            for msg in messages_copy:
                lines.append(f"{msg.role.upper()}: {msg.content}")
            return "\n".join(lines)

    def clear(self) -> None:
        """Clear all messages from the session (thread-safe)."""
        with self._lock:
            self._messages.clear()

    def get_token_count(self) -> int:
        """Get approximate token count for current context.

        Uses a simple heuristic: ~4 characters per token (typical for English text).

        Returns:
            Approximate number of tokens
        """
        with self._lock:
            total_chars = sum(len(msg.content) for msg in self._messages)

        # Approximate: 4 characters per token (conservative estimate)
        return total_chars // 4
