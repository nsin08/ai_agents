"""
RAG memory implementation with mock embeddings and similarity search.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from .base import Memory, MemoryItem


class RAGMemory(Memory):
    """RAG memory with mock embeddings and cosine similarity."""

    def __init__(self, embedding_dim: int = 8) -> None:
        if embedding_dim <= 0:
            raise ValueError("embedding_dim must be positive")
        self._items: List[MemoryItem] = []
        self._embedding_dim = embedding_dim

    def store(self, item: MemoryItem) -> None:
        if item.embedding is None:
            item.embedding = self._embed(item.content)
        self._items.append(item)

    def retrieve(self, query: Optional[str] = None, top_k: int = 5, **kwargs) -> List[MemoryItem]:
        if not query:
            return list(self._items)
        query_embedding = self._embed(query)
        scored: List[Tuple[float, MemoryItem]] = [
            (self._cosine_similarity(query_embedding, item.embedding or []), item)
            for item in self._items
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def clear(self) -> None:
        self._items.clear()

    def _embed(self, text: str) -> List[float]:
        """Generate a deterministic mock embedding from text."""
        buckets = [0] * self._embedding_dim
        for index, char in enumerate(text):
            buckets[index % self._embedding_dim] += ord(char)
        total = sum(buckets) or 1
        return [value / total for value in buckets]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
