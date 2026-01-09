"""
Chunking strategies for context engineering.
"""

from __future__ import annotations

from typing import List


def chunk_fixed(text: str, size: int = 500) -> List[str]:
    """Split text into fixed-size chunks."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [text[i : i + size] for i in range(0, len(text), size)]


def chunk_sliding(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")
    chunks = []
    step = size - overlap
    for i in range(0, len(text), step):
        chunk = text[i : i + size]
        if chunk:
            chunks.append(chunk)
        if i + size >= len(text):
            break
    return chunks


def chunk_semantic_mock(text: str, max_chars: int = 600) -> List[str]:
    """Mock semantic chunking by splitting on sentence boundaries."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    chunks = []
    current = []
    current_len = 0
    for sentence in sentences:
        candidate = f"{sentence}."
        if current_len + len(candidate) > max_chars and current:
            chunks.append(" ".join(current))
            current = [candidate]
            current_len = len(candidate)
        else:
            current.append(candidate)
            current_len += len(candidate)
    if current:
        chunks.append(" ".join(current))
    return chunks
