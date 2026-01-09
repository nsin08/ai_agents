"""
Memory manager coordinating short-term, long-term, and RAG memory tiers.
"""

from typing import List, Optional

from .base import MemoryItem
from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .rag import RAGMemory


class MemoryManager:
    """Coordinator for memory tiers with simple integration hooks."""

    def __init__(
        self,
        short_term: Optional[ShortTermMemory] = None,
        long_term: Optional[LongTermMemory] = None,
        rag: Optional[RAGMemory] = None,
    ) -> None:
        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term or LongTermMemory()
        self.rag = rag or RAGMemory()

    def store_short(self, item: MemoryItem) -> None:
        self.short_term.store(item)

    def store_long(self, item: MemoryItem, key: Optional[str] = None) -> None:
        self.long_term.store(item, key=key)

    def store_rag(self, item: MemoryItem) -> None:
        self.rag.store(item)

    def retrieve_short(self, query: Optional[str] = None, **kwargs) -> List[MemoryItem]:
        return self.short_term.retrieve(query=query, **kwargs)

    def retrieve_long(self, query: Optional[str] = None, **kwargs) -> List[MemoryItem]:
        return self.long_term.retrieve(query=query, **kwargs)

    def retrieve_rag(self, query: Optional[str] = None, **kwargs) -> List[MemoryItem]:
        return self.rag.retrieve(query=query, **kwargs)

    def observe(self, query: Optional[str] = None) -> dict:
        """Retrieve memory for the Observe step."""
        return {
            "short_term": self.retrieve_short(query=query),
            "long_term": self.retrieve_long(query=query),
            "rag": self.retrieve_rag(query=query),
        }

    def refine(self, items: List[MemoryItem]) -> None:
        """Store memory items on Refine step."""
        for item in items:
            self.store_short(item)
            self.store_long(item)
            self.store_rag(item)

    def clear(self) -> None:
        self.short_term.clear()
        self.long_term.clear()
        self.rag.clear()
