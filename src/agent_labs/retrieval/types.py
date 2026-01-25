"""Retrieval types (vector + metadata + provenance).

These types are designed for educational and offline-testable labs:
- chunk ingestion (doc_id/chunk_id/text/metadata)
- query-time results with scores and provenance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ChunkRecord:
    """A single chunk stored in an index."""

    doc_id: str
    chunk_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class RetrievedChunk:
    """A retrieved chunk with relevance score and provenance."""

    doc_id: str
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None

