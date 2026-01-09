# Memory Systems

Pluggable memory tiers that store and retrieve context for agent workflows.

## Memory Tiers

1. Short-term: bounded, turn-by-turn history.
2. Long-term: persistent key-value storage.
3. RAG: semantic retrieval with mock embeddings.

## Architecture

```
Agent Observe -> MemoryManager.observe()
Agent Refine  -> MemoryManager.refine()
```

## Modules

- `base.py`: Memory base class + `MemoryItem`.
- `short_term.py`: Short-term memory (deque).
- `long_term.py`: Long-term memory (pluggable storage).
- `rag.py`: RAG memory (mock embeddings).
- `storage.py`: Storage backends (in-memory, sqlite, vector store stubs).
- `manager.py`: Coordinator for all tiers.

## Usage

```python
from agent_labs.memory import MemoryItem, MemoryManager

manager = MemoryManager()
item = MemoryItem(content="User prefers concise answers", metadata={"source": "chat"})

# Store across tiers
manager.refine([item])

# Retrieve during observe
memory = manager.observe(query="concise")
short_term = memory["short_term"]
```

## Retrieval Strategies

- Short-term: substring match over recent items.
- Long-term: backend search (in-memory substring, sqlite LIKE).
- RAG: cosine similarity over mock embeddings.

## Notes

- Embeddings are deterministic and mock (no external model calls).
- SQLite backend uses a local file; keep it in `.context/` or a lab folder.
- Vector store adapters are stubbed for future ChromaDB integration.
