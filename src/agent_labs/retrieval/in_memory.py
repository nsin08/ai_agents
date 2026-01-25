"""Deterministic in-memory vector index (offline-testable).

This uses a deterministic embedding function and cosine similarity.
It is not a production vector DB, but it is useful for labs and unit tests.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .types import ChunkRecord, RetrievedChunk


@dataclass
class DeterministicEmbedder:
    """Generate deterministic mock embeddings from text."""

    embedding_dim: int = 8

    def embed(self, text: str) -> List[float]:
        if self.embedding_dim <= 0:
            raise ValueError("embedding_dim must be positive")
        buckets = [0] * self.embedding_dim
        for index, char in enumerate(text):
            buckets[index % self.embedding_dim] += ord(char)
        total = sum(buckets) or 1
        return [value / total for value in buckets]


class InMemoryVectorIndex:
    """Vector index with simple metadata filters."""

    def __init__(self, *, embedder: Optional[DeterministicEmbedder] = None) -> None:
        self._embedder = embedder or DeterministicEmbedder()
        self._items: List[Tuple[ChunkRecord, List[float]]] = []

    def clear(self) -> None:
        self._items.clear()

    def upsert(self, records: List[ChunkRecord]) -> None:
        for record in records:
            embedding = self._embedder.embed(record.text)
            self._items.append((record, embedding))

    def query(
        self,
        query_text: str,
        *,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        if top_k <= 0:
            return []

        query_embedding = self._embedder.embed(query_text)
        candidates: List[Tuple[float, ChunkRecord]] = []
        for record, embedding in self._items:
            if not self._matches_filters(record, filters):
                continue
            score = self._cosine_similarity(query_embedding, embedding)
            candidates.append((score, record))

        candidates.sort(key=lambda pair: pair[0], reverse=True)
        results: List[RetrievedChunk] = []
        for score, record in candidates[:top_k]:
            results.append(
                RetrievedChunk(
                    doc_id=record.doc_id,
                    chunk_id=record.chunk_id,
                    text=record.text,
                    score=float(score),
                    metadata=dict(record.metadata),
                    timestamp=record.timestamp,
                )
            )
        return results

    @staticmethod
    def _matches_filters(record: ChunkRecord, filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        for key, expected in filters.items():
            actual = record.metadata.get(key)
            if isinstance(expected, (list, tuple, set)):
                if actual not in expected:
                    return False
            else:
                if actual != expected:
                    return False
        return True

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

