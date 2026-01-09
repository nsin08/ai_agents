"""
Long-term memory implementation with pluggable storage backends.
"""

from typing import List, Optional

from .base import Memory, MemoryItem
from .storage import StorageBackend, InMemoryStorage, SqliteStorage


class LongTermMemory(Memory):
    """Long-term memory backed by a storage backend."""

    def __init__(self, backend: Optional[StorageBackend] = None) -> None:
        self._backend = backend or InMemoryStorage()

    @property
    def backend(self) -> StorageBackend:
        return self._backend

    def store(self, item: MemoryItem, key: Optional[str] = None) -> None:
        storage_key = key or item.metadata.get("key") or item.content[:32]
        self._backend.store(storage_key, item)

    def retrieve(self, query: Optional[str] = None, limit: int = 10, **kwargs) -> List[MemoryItem]:
        if not query:
            return list(self._backend.iter_items())
        return self._backend.search(query, limit=limit)

    def get(self, key: str) -> Optional[MemoryItem]:
        return self._backend.get(key)

    def clear(self) -> None:
        self._backend.clear()


def sqlite_backend(path: str = "memory.db") -> SqliteStorage:
    """Convenience factory for SQLite backend."""
    return SqliteStorage(path=path)
