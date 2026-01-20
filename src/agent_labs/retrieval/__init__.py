"""Retrieval utilities (vector index + provenance types)."""

from .base import VectorIndex
from .in_memory import DeterministicEmbedder, InMemoryVectorIndex
from .types import ChunkRecord, RetrievedChunk

__all__ = [
    "VectorIndex",
    "DeterministicEmbedder",
    "InMemoryVectorIndex",
    "ChunkRecord",
    "RetrievedChunk",
]

