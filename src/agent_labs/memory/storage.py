"""
Storage backends for long-term memory.
"""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from .base import MemoryItem


class StorageBackend(ABC):
    """Abstract storage backend for long-term memory."""

    @abstractmethod
    def store(self, key: str, item: MemoryItem) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> Optional[MemoryItem]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def iter_items(self) -> Iterable[MemoryItem]:
        raise NotImplementedError


class VectorStoreBackend(ABC):
    """Abstract vector store backend for RAG memory."""

    @abstractmethod
    def add(self, item: MemoryItem) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, embedding: List[float], top_k: int = 5) -> List[MemoryItem]:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


class ChromaVectorStore(VectorStoreBackend):
    """Placeholder adapter for future ChromaDB integration."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "ChromaVectorStore is a placeholder. Install chromadb and implement adapter in Phase 2."
        )

    def add(self, item: MemoryItem) -> None:
        raise NotImplementedError("ChromaVectorStore is not implemented.")

    def query(self, embedding: List[float], top_k: int = 5) -> List[MemoryItem]:
        raise NotImplementedError("ChromaVectorStore is not implemented.")

    def clear(self) -> None:
        raise NotImplementedError("ChromaVectorStore is not implemented.")


@dataclass
class InMemoryStorage(StorageBackend):
    """In-memory dictionary storage backend."""

    def __init__(self) -> None:
        self._items: Dict[str, MemoryItem] = {}

    def store(self, key: str, item: MemoryItem) -> None:
        self._items[key] = item

    def get(self, key: str) -> Optional[MemoryItem]:
        return self._items.get(key)

    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        query_lower = query.lower()
        matches = [
            item for item in self._items.values()
            if query_lower in item.content.lower()
        ]
        return matches[:limit]

    def clear(self) -> None:
        self._items.clear()

    def iter_items(self) -> Iterable[MemoryItem]:
        return list(self._items.values())


class SqliteStorage(StorageBackend):
    """SQLite storage backend for long-term memory."""

    def __init__(self, path: str = "memory.db") -> None:
        self._path = path
        self._conn = sqlite3.connect(self._path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_items (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
            """
        )
        self._conn.commit()

    def store(self, key: str, item: MemoryItem) -> None:
        self._conn.execute(
            """
            INSERT INTO memory_items (key, content, timestamp, metadata)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                content = excluded.content,
                timestamp = excluded.timestamp,
                metadata = excluded.metadata
            """,
            (key, item.content, item.timestamp.isoformat(), json.dumps(item.metadata)),
        )
        self._conn.commit()

    def get(self, key: str) -> Optional[MemoryItem]:
        cursor = self._conn.execute(
            "SELECT content, timestamp, metadata FROM memory_items WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        content, timestamp, metadata_json = row
        metadata = json.loads(metadata_json) if metadata_json else {}
        return MemoryItem(
            content=content,
            timestamp=datetime.fromisoformat(timestamp),
            metadata=metadata,
        )

    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        cursor = self._conn.execute(
            """
            SELECT content, timestamp, metadata
            FROM memory_items
            WHERE content LIKE ?
            LIMIT ?
            """,
            (f"%{query}%", limit),
        )
        results = []
        for content, timestamp, metadata_json in cursor.fetchall():
            metadata = json.loads(metadata_json) if metadata_json else {}
            results.append(
                MemoryItem(
                    content=content,
                    timestamp=datetime.fromisoformat(timestamp),
                    metadata=metadata,
                )
            )
        return results

    def clear(self) -> None:
        self._conn.execute("DELETE FROM memory_items")
        self._conn.commit()

    def iter_items(self) -> Iterable[MemoryItem]:
        cursor = self._conn.execute(
            "SELECT content, timestamp, metadata FROM memory_items"
        )
        results = []
        for content, timestamp, metadata_json in cursor.fetchall():
            metadata = json.loads(metadata_json) if metadata_json else {}
            results.append(
                MemoryItem(
                    content=content,
                    timestamp=datetime.fromisoformat(timestamp),
                    metadata=metadata,
                )
            )
        return results

    def close(self) -> None:
        """Close the SQLite connection."""
        self._conn.close()

    def __del__(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
