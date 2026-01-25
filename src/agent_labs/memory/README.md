# Memory Systems

Pluggable memory tiers that store and retrieve context for agent workflows.

## Memory Tiers

1. Short-term: bounded, turn-by-turn history.
2. Long-term: persistent key-value storage.
3. RAG: semantic retrieval with mock embeddings.
4. Session-based: conversational context with thread-safety.

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
- `session.py`: Session-based conversation memory with thread-safety.

## Usage

### Memory Manager

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

### Session Store (Conversational Memory)

```python
from agent_labs.memory import InMemorySessionStore

# Create a session store with max 20 turns
session = InMemorySessionStore(max_turns=20)

# Add messages
session.add_message("user", "What is Python?")
session.add_message("assistant", "Python is a programming language...")
session.add_message("user", "How do I install it?")

# Get context for LLM
context = session.get_context(format="list")  # List of dicts
# or
context_str = session.get_context(format="string")  # Formatted string

# Check token count
tokens = session.get_token_count()

# Clear session
session.clear()
```

## Retrieval Strategies

- Short-term: substring match over recent items.
- Long-term: backend search (in-memory substring, sqlite LIKE).
- RAG: cosine similarity over mock embeddings.
- Session: thread-safe conversation history with max_turns enforcement.

## Notes

- Embeddings are deterministic and mock (no external model calls).
- SQLite backend uses a local file; keep it in `.context/` or a lab folder.
- Vector store adapters are stubbed for future ChromaDB integration.
- Session store uses threading.Lock for thread-safe operations.
- Token counting uses a simple heuristic (~4 chars per token).
