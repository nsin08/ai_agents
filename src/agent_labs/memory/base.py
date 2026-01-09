"""
Memory base abstractions and shared data structures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class MemoryItem:
    """Structured memory item shared across memory tiers."""

    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize a memory item to a dictionary."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "embedding": self.embedding,
        }


class Memory(ABC):
    """Abstract base class for memory tiers."""

    @abstractmethod
    def store(self, item: MemoryItem) -> None:
        """Store a memory item."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, query: Optional[str] = None, **kwargs: Any) -> List[MemoryItem]:
        """Retrieve memory items based on a query."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Clear memory."""
        raise NotImplementedError

    def iter_items(self) -> Iterable[MemoryItem]:
        """Optional iterator over items (defaults to retrieve all)."""
        return self.retrieve()
