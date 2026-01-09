"""
Unit tests for memory systems (short-term, long-term, RAG).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.agent_labs.memory import (
    MemoryItem,
    ShortTermMemory,
    LongTermMemory,
    RAGMemory,
    MemoryManager,
    InMemoryStorage,
    SqliteStorage,
    ChromaVectorStore,
)


def test_memory_item_to_dict():
    item = MemoryItem(content="test", metadata={"source": "unit"})
    data = item.to_dict()

    assert data["content"] == "test"
    assert data["metadata"]["source"] == "unit"
    assert "timestamp" in data


def test_short_term_memory_store_and_retrieve():
    memory = ShortTermMemory(max_items=2)
    item1 = MemoryItem(content="first")
    item2 = MemoryItem(content="second")
    item3 = MemoryItem(content="third")

    memory.store(item1)
    memory.store(item2)
    memory.store(item3)

    results = memory.retrieve()
    assert len(results) == 2
    assert results[0].content == "second"
    assert results[1].content == "third"


def test_short_term_memory_query():
    memory = ShortTermMemory(max_items=5)
    memory.store(MemoryItem(content="hello world"))
    memory.store(MemoryItem(content="another item"))

    results = memory.retrieve(query="hello")
    assert len(results) == 1
    assert results[0].content == "hello world"


def test_short_term_memory_invalid_size():
    with pytest.raises(ValueError):
        ShortTermMemory(max_items=0)


def test_long_term_memory_in_memory_backend():
    memory = LongTermMemory(backend=InMemoryStorage())
    item = MemoryItem(content="persisted", metadata={"key": "k1"})

    memory.store(item)
    fetched = memory.get("k1")

    assert fetched is not None
    assert fetched.content == "persisted"


def test_long_term_memory_search():
    memory = LongTermMemory(backend=InMemoryStorage())
    memory.store(MemoryItem(content="alpha memory"))
    memory.store(MemoryItem(content="beta memory"))

    results = memory.retrieve(query="alpha")
    assert len(results) == 1
    assert results[0].content == "alpha memory"


def test_long_term_memory_sqlite_backend():
    with TemporaryDirectory() as temp_dir:
        db_path = str(Path(temp_dir) / "memory.db")
        backend = SqliteStorage(path=db_path)
        memory = LongTermMemory(backend=backend)
        item = MemoryItem(content="sqlite item", timestamp=datetime.utcnow())

        memory.store(item, key="row1")
        fetched = memory.get("row1")

        assert fetched is not None
        assert fetched.content == "sqlite item"

        results = memory.retrieve(query="sqlite")
        assert len(results) == 1

        memory.clear()
        assert memory.retrieve() == []
        backend.close()


def test_rag_memory_retrieval():
    memory = RAGMemory(embedding_dim=4)
    memory.store(MemoryItem(content="alpha"))
    memory.store(MemoryItem(content="beta"))
    memory.store(MemoryItem(content="gamma"))

    results = memory.retrieve(query="alpha", top_k=2)
    assert len(results) == 2
    assert results[0].content in {"alpha", "gamma", "beta"}


def test_rag_memory_invalid_dim():
    with pytest.raises(ValueError):
        RAGMemory(embedding_dim=0)


def test_memory_manager_observe_and_refine():
    manager = MemoryManager()
    item = MemoryItem(content="remember this", metadata={"source": "unit"})

    manager.refine([item])
    memory = manager.observe(query="remember")

    assert "short_term" in memory
    assert "long_term" in memory
    assert "rag" in memory
    assert len(memory["short_term"]) >= 1
    assert len(memory["long_term"]) >= 1
    assert len(memory["rag"]) >= 1


def test_chroma_vector_store_placeholder():
    with pytest.raises(NotImplementedError):
        ChromaVectorStore()
