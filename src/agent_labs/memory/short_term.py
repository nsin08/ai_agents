"""
Short-term memory implementation (bounded, turn-by-turn).
"""

from collections import deque
from typing import List, Optional

from .base import Memory, MemoryItem


class ShortTermMemory(Memory):
    """Short-term memory stored in a bounded deque."""

    def __init__(self, max_items: int = 20) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be positive")
        self._items = deque(maxlen=max_items)

    def store(self, item: MemoryItem) -> None:
        self._items.append(item)

    def retrieve(self, query: Optional[str] = None, **kwargs) -> List[MemoryItem]:
        items = list(self._items)
        if not query:
            return items
        query_lower = query.lower()
        return [item for item in items if query_lower in item.content.lower()]

    def clear(self) -> None:
        self._items.clear()
