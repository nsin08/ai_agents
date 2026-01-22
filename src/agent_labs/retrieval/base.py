"""Retrieval interfaces.

VectorIndex is intentionally minimal so labs can use a deterministic in-memory
implementation while production backends can be added later.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from .types import ChunkRecord, RetrievedChunk


class VectorIndex(Protocol):
    """Vector index interface with metadata filtering."""

    def upsert(self, records: List[ChunkRecord]) -> None:
        """Insert or update chunk records."""

    def query(
        self,
        query_text: str,
        *,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        """Query by text and optional metadata filters."""

    def clear(self) -> None:
        """Remove all indexed chunks."""

