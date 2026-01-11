"""
Memory agent implementation for Lab 4.

Demonstrates memory management across short-term, long-term, and RAG memory tiers.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.agent_labs.memory import MemoryItem, ShortTermMemory, LongTermMemory


@dataclass
class Fact:
    """A fact with a confidence score for long-term memory."""

    content: str
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_memory_item(self) -> MemoryItem:
        """Convert fact to MemoryItem."""
        return MemoryItem(
            content=self.content,
            timestamp=self.timestamp,
            metadata={**self.metadata, "confidence": self.confidence},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize fact to dictionary."""
        return {
            "content": self.content,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Fact:
        """Deserialize fact from dictionary."""
        return cls(
            content=data["content"],
            confidence=data.get("confidence", 1.0),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RetrievalTrace:
    """Trace information about memory retrieval."""

    query: str
    short_term_items: List[MemoryItem]
    long_term_items: List[MemoryItem]
    retrieval_time_ms: float
    relevance_scores: Dict[str, float] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format trace for display."""
        lines = [
            f"\n=== Memory Retrieval Trace ===",
            f"Query: {self.query}",
            f"Retrieval time: {self.retrieval_time_ms:.2f}ms",
            f"\nShort-term memory ({len(self.short_term_items)} items):",
        ]
        for item in self.short_term_items:
            lines.append(f"  - {item.content[:80]}...")
        
        lines.append(f"\nLong-term memory ({len(self.long_term_items)} items):")
        for item in self.long_term_items:
            confidence = item.metadata.get("confidence", 1.0)
            lines.append(f"  - {item.content[:80]}... (confidence: {confidence:.2f})")
        
        if self.relevance_scores:
            lines.append("\nRelevance scores:")
            for content, score in self.relevance_scores.items():
                lines.append(f"  - {content[:50]}...: {score:.3f}")
        
        lines.append("=" * 30)
        return "\n".join(lines)


class MemoryAgent:
    """Agent with configurable memory tiers for multi-turn conversations."""

    def __init__(self, max_short_term: int = 10) -> None:
        """Initialize memory agent.

        Args:
            max_short_term: Maximum number of items in short-term memory (default 10)
        """
        if max_short_term <= 0:
            raise ValueError("max_short_term must be positive")
        
        self.short_term = ShortTermMemory(max_items=max_short_term)
        self.long_term = LongTermMemory()
        self.max_short_term = max_short_term

    def add_conversation_turn(self, role: str, content: str) -> None:
        """Add a conversation turn to short-term memory.

        Args:
            role: Role of the speaker (e.g., 'user', 'assistant')
            content: Content of the message
        """
        item = MemoryItem(
            content=content,
            metadata={"role": role, "type": "conversation"},
        )
        self.short_term.store(item)

    def add_fact(self, content: str, confidence: float = 1.0, key: Optional[str] = None) -> None:
        """Add a fact to long-term memory.

        Args:
            content: Fact content
            confidence: Confidence score (0.0 to 1.0)
            key: Optional key for the fact (defaults to first 32 chars of content)
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        fact = Fact(content=content, confidence=confidence)
        item = fact.to_memory_item()
        storage_key = key or content[:32]
        self.long_term.store(item, key=storage_key)

    def retrieve(self, query: str, include_trace: bool = False) -> List[MemoryItem]:
        """Retrieve relevant memories based on query.

        Args:
            query: Search query
            include_trace: Whether to return trace information

        Returns:
            List of relevant memory items
        """
        start_time = time.time()
        
        # Split query into terms for matching
        query_terms = set(query.lower().split())
        
        # Retrieve from short-term memory - check each item for relevance
        short_term_all = self.short_term.retrieve()
        short_term_items = []
        for item in short_term_all:
            content_terms = set(item.content.lower().split())
            if query_terms & content_terms:  # If any query term matches
                short_term_items.append(item)
        
        # Retrieve from long-term memory - check each fact for relevance
        long_term_all = self.long_term.retrieve()
        long_term_items = []
        for item in long_term_all:
            content_terms = set(item.content.lower().split())
            if query_terms & content_terms:  # If any query term matches
                long_term_items.append(item)
        
        # Limit long-term results
        long_term_items = long_term_items[:5]
        
        retrieval_time_ms = (time.time() - start_time) * 1000
        
        # Calculate simple relevance scores based on query term matches
        relevance_scores = {}
        
        all_items = short_term_items + long_term_items
        for item in all_items:
            content_terms = set(item.content.lower().split())
            matches = len(query_terms & content_terms)
            if matches > 0:
                relevance_scores[item.content] = matches / len(query_terms)
        
        if include_trace:
            trace = RetrievalTrace(
                query=query,
                short_term_items=short_term_items,
                long_term_items=long_term_items,
                retrieval_time_ms=retrieval_time_ms,
                relevance_scores=relevance_scores,
            )
            print(trace)
        
        return all_items

    def get_all_facts(self) -> List[Fact]:
        """Retrieve all facts from long-term memory.

        Returns:
            List of all facts
        """
        items = self.long_term.retrieve()
        facts = []
        for item in items:
            confidence = item.metadata.get("confidence", 1.0)
            facts.append(
                Fact(
                    content=item.content,
                    confidence=confidence,
                    timestamp=item.timestamp,
                    metadata={k: v for k, v in item.metadata.items() if k != "confidence"},
                )
            )
        return facts

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history from short-term memory.

        Returns:
            List of conversation turns with role and content
        """
        items = self.short_term.retrieve()
        history = []
        for item in items:
            if item.metadata.get("type") == "conversation":
                history.append({
                    "role": item.metadata.get("role", "unknown"),
                    "content": item.content,
                })
        return history

    def save_to_json(self, path: str) -> None:
        """Save memory state to JSON file.

        Args:
            path: Path to JSON file
        """
        data = {
            "max_short_term": self.max_short_term,
            "short_term": [
                item.to_dict() for item in self.short_term.retrieve()
            ],
            "long_term": [
                fact.to_dict() for fact in self.get_all_facts()
            ],
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> MemoryAgent:
        """Load memory state from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            MemoryAgent instance with loaded state
        """
        with open(path, "r") as f:
            data = json.load(f)
        
        agent = cls(max_short_term=data.get("max_short_term", 10))
        
        # Restore short-term memory
        for item_data in data.get("short_term", []):
            item = MemoryItem(
                content=item_data["content"],
                timestamp=datetime.fromisoformat(item_data["timestamp"]),
                metadata=item_data.get("metadata", {}),
            )
            agent.short_term.store(item)
        
        # Restore long-term memory
        for fact_data in data.get("long_term", []):
            fact = Fact.from_dict(fact_data)
            agent.long_term.store(
                fact.to_memory_item(),
                key=fact.content[:32],
            )
        
        return agent

    def clear(self) -> None:
        """Clear all memory tiers."""
        self.short_term.clear()
        self.long_term.clear()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage.

        Returns:
            Dictionary with memory statistics
        """
        short_items = self.short_term.retrieve()
        long_items = self.long_term.retrieve()
        
        return {
            "short_term_count": len(short_items),
            "short_term_max": self.max_short_term,
            "short_term_usage": len(short_items) / self.max_short_term,
            "long_term_count": len(long_items),
            "total_items": len(short_items) + len(long_items),
        }
