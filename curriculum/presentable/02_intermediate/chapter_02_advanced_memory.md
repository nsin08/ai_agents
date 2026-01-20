# Chapter 02: Advanced Memory Systems

[Prev](chapter_01_orchestrator_patterns.md) | [Up](README.md) | [Next](chapter_03_context_engineering.md)

---

## Learning Objectives

After completing this chapter, you will be able to:

1. **Understand Memory Tiers** — Explain the purpose and trade-offs of short-term, long-term, and RAG memory systems
2. **Implement Episodic vs. Semantic Memory** — Distinguish between conversation-based (episodic) and fact-based (semantic) storage strategies
3. **Design Retrieval Strategies** — Build relevance-based retrieval with confidence scoring and trace output
4. **Manage Memory Lifecycle** — Handle FIFO pruning, capacity limits, and persistence across sessions
5. **Integrate Memory with Agents** — Connect memory systems to the orchestrator for context-aware responses

---

## Introduction

Memory is what transforms a stateless chatbot into a contextual assistant. Without memory, every interaction starts from scratch—the agent has no idea what you discussed a minute ago, let alone last week.

This chapter explores the memory architecture implemented in `src/agent_labs/memory/` and demonstrated in Lab 4. You'll learn to build multi-tier memory systems that balance speed (short-term), permanence (long-term), and semantic understanding (RAG).

**Key Insight:** Memory isn't just storage—it's a retrieval strategy. The right memory architecture depends on *what* you need to remember and *how quickly* you need to access it.

---

## 1. Memory Architecture Overview

### 1.1 Three-Tier Memory System

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MEMORY ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                   SHORT-TERM MEMORY                         │     │
│  │  • Bounded conversational context (FIFO)                   │     │
│  │  • Fast access: O(1) append, O(n) search                   │     │
│  │  • Capacity: 10-50 items typical                           │     │
│  │  • Use case: Recent conversation turns                     │     │
│  └────────────────────────────────────────────────────────────┘     │
│                          ↓ overflow / summarize                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                   LONG-TERM MEMORY                          │     │
│  │  • Persistent facts with confidence scores                 │     │
│  │  • Key-value storage with search                           │     │
│  │  • Capacity: Unlimited (backend-dependent)                 │     │
│  │  • Use case: User preferences, extracted entities          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                          ↓ semantic queries                          │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    RAG MEMORY (Future)                      │     │
│  │  • Vector embeddings for semantic search                   │     │
│  │  • Similarity-based retrieval                              │     │
│  │  • Capacity: Documents, knowledge bases                    │     │
│  │  • Use case: Complex knowledge retrieval                   │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 When to Use Each Tier

| Memory Tier | Access Speed | Persistence | Best For |
|-------------|-------------|-------------|----------|
| **Short-term** | ~0.01ms | Session only | Recent conversation turns |
| **Long-term** | ~1-5ms | Cross-session | User facts, preferences |
| **RAG** | ~50-200ms | Indexed docs | Knowledge retrieval |

### 1.3 Memory Item Structure

All memory tiers share a common data structure:

```python
# From src/agent_labs/memory/base.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class MemoryItem:
    """Structured memory item shared across memory tiers."""

    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # For RAG tier

    def to_dict(self) -> Dict[str, Any]:
        """Serialize a memory item to a dictionary."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "embedding": self.embedding,
        }
```

**Design Pattern:** The unified `MemoryItem` structure allows items to flow between tiers (e.g., a conversation turn that becomes a long-term fact) without data transformation.

---

## 2. Episodic vs. Semantic Memory

### 2.1 Cognitive Science Background

Human memory research distinguishes two key types:

- **Episodic Memory:** Autobiographical events with temporal context ("Last Tuesday, the user asked about Seattle weather")
- **Semantic Memory:** General knowledge without temporal context ("User lives in Seattle")

AI agents benefit from both patterns.

### 2.2 Episodic Memory: Conversation History

Episodic memory captures *what happened* in sequence. In agent systems, this maps to conversation history:

```python
# Episodic memory: preserves temporal order and context
class ShortTermMemory(Memory):
    """Short-term memory stored in a bounded deque."""

    def __init__(self, max_items: int = 20) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be positive")
        self._items = deque(maxlen=max_items)  # FIFO when full

    def store(self, item: MemoryItem) -> None:
        self._items.append(item)  # O(1) append

    def retrieve(self, query: Optional[str] = None) -> List[MemoryItem]:
        items = list(self._items)
        if not query:
            return items  # All items in temporal order
        query_lower = query.lower()
        return [item for item in items if query_lower in item.content.lower()]
```

**Key Property:** Episodic memory preserves *order*. When retrieved, items appear in the sequence they were stored—essential for understanding conversation flow.

### 2.3 Semantic Memory: Facts and Knowledge

Semantic memory extracts *what is true* from episodes. Facts are stored with confidence scores:

```python
# Semantic memory: facts with confidence
@dataclass
class Fact:
    """A fact with a confidence score for long-term memory."""

    content: str
    confidence: float = 1.0  # 0.0 = uncertain, 1.0 = certain
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Usage: Extract facts from conversation
def extract_facts_from_episode(conversation: List[MemoryItem]) -> List[Fact]:
    """Extract semantic facts from episodic memory."""
    facts = []
    
    for item in conversation:
        if "I live in" in item.content:
            location = item.content.split("I live in")[-1].strip()
            facts.append(Fact(content=f"User lives in {location}", confidence=1.0))
        
        if "I like" in item.content:
            preference = item.content.split("I like")[-1].strip()
            facts.append(Fact(content=f"User likes {preference}", confidence=0.9))
    
    return facts
```

### 2.4 Memory Consolidation Pattern

In production agents, episodic memories should periodically consolidate into semantic facts:

```
┌──────────────────┐     Extraction      ┌──────────────────┐
│ Episodic Memory  │ ──────────────────▶ │ Semantic Memory  │
│                  │                      │                  │
│ "I live in NYC"  │      ▶              │ lives_in: NYC    │
│ "I like coffee"  │      ▶              │ likes: coffee    │
│ "Hello"          │      (ignored)      │                  │
│ "Weather?"       │      (ignored)      │                  │
└──────────────────┘                      └──────────────────┘
```

```python
# Example: Memory consolidation during session end
async def consolidate_session(agent: MemoryAgent) -> int:
    """Extract facts from conversation and store in long-term memory."""
    history = agent.get_conversation_history()
    
    # Convert to MemoryItems for processing
    items = [MemoryItem(content=turn["content"], metadata={"role": turn["role"]}) 
             for turn in history]
    
    # Extract facts (in production, use LLM for extraction)
    facts = extract_facts_from_episode(items)
    
    # Store in long-term memory
    for fact in facts:
        agent.add_fact(fact.content, confidence=fact.confidence)
    
    return len(facts)
```

---

## 3. Short-Term Memory Implementation

### 3.1 Bounded Deque Pattern

Short-term memory uses a bounded deque (double-ended queue) for efficient FIFO behavior:

```python
from collections import deque
from typing import List, Optional

class ShortTermMemory(Memory):
    """Short-term memory stored in a bounded deque."""

    def __init__(self, max_items: int = 20) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be positive")
        self._items = deque(maxlen=max_items)

    def store(self, item: MemoryItem) -> None:
        """Append item; oldest item auto-removed if at capacity."""
        self._items.append(item)

    def retrieve(self, query: Optional[str] = None, **kwargs) -> List[MemoryItem]:
        """Return all items or filter by query."""
        items = list(self._items)
        if not query:
            return items
        query_lower = query.lower()
        return [item for item in items if query_lower in item.content.lower()]

    def clear(self) -> None:
        """Clear all items."""
        self._items.clear()
```

### 3.2 FIFO Pruning Behavior

When short-term memory reaches capacity, the oldest items are automatically discarded:

```python
# FIFO pruning demonstration
agent = MemoryAgent(max_short_term=3)

agent.add_conversation_turn("user", "Message 0")  # Stored
agent.add_conversation_turn("user", "Message 1")  # Stored
agent.add_conversation_turn("user", "Message 2")  # Stored (full)
agent.add_conversation_turn("user", "Message 3")  # Message 0 pruned
agent.add_conversation_turn("user", "Message 4")  # Message 1 pruned

# Result: Only ["Message 2", "Message 3", "Message 4"] remain
history = agent.get_conversation_history()
assert len(history) == 3
assert history[0]["content"] == "Message 2"
```

### 3.3 Choosing max_items

| Use Case | Recommended max_items | Rationale |
|----------|----------------------|-----------|
| Quick Q&A | 5-10 | Low context needed |
| Multi-turn support | 20-30 | Need to reference earlier turns |
| Code assistance | 50+ | Large code context |
| Summarization | 10 + summary buffer | Summarize before pruning |

**Best Practice:** Start with 10-20 items. Monitor token usage in production—if hitting context limits, reduce max_items or implement summarization.

---

## 4. Long-Term Memory Implementation

### 4.1 Storage Backend Abstraction

Long-term memory uses pluggable storage backends:

```python
# From src/agent_labs/memory/storage.py
from abc import ABC, abstractmethod
from typing import List, Optional, Iterable

class StorageBackend(ABC):
    """Abstract storage backend for long-term memory."""

    @abstractmethod
    def store(self, key: str, item: MemoryItem) -> None:
        """Store an item by key."""
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[MemoryItem]:
        """Retrieve an item by key."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search items by query."""
        pass

    @abstractmethod
    def iter_items(self) -> Iterable[MemoryItem]:
        """Iterate over all items."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all items."""
        pass
```

### 4.2 In-Memory Backend (Development)

For development and testing, use the in-memory backend:

```python
class InMemoryStorage(StorageBackend):
    """In-memory storage backend (development/testing)."""

    def __init__(self) -> None:
        self._items: Dict[str, MemoryItem] = {}

    def store(self, key: str, item: MemoryItem) -> None:
        self._items[key] = item

    def get(self, key: str) -> Optional[MemoryItem]:
        return self._items.get(key)

    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        query_lower = query.lower()
        matches = [item for item in self._items.values() 
                   if query_lower in item.content.lower()]
        return matches[:limit]

    def iter_items(self) -> Iterable[MemoryItem]:
        return self._items.values()

    def clear(self) -> None:
        self._items.clear()
```

### 4.3 SQLite Backend (Production)

For production, use SQLite for persistence:

```python
import sqlite3
from pathlib import Path

class SqliteStorage(StorageBackend):
    """SQLite storage backend (production)."""

    def __init__(self, path: str = "memory.db") -> None:
        self._path = path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self._path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                embedding BLOB
            )
        """)
        conn.commit()
        conn.close()

    def store(self, key: str, item: MemoryItem) -> None:
        conn = sqlite3.connect(self._path)
        conn.execute("""
            INSERT OR REPLACE INTO memory (key, content, timestamp, metadata)
            VALUES (?, ?, ?, ?)
        """, (key, item.content, item.timestamp.isoformat(), 
              json.dumps(item.metadata)))
        conn.commit()
        conn.close()
```

### 4.4 Long-Term Memory Class

The `LongTermMemory` class wraps the storage backend:

```python
class LongTermMemory(Memory):
    """Long-term memory backed by a storage backend."""

    def __init__(self, backend: Optional[StorageBackend] = None) -> None:
        self._backend = backend or InMemoryStorage()

    def store(self, item: MemoryItem, key: Optional[str] = None) -> None:
        """Store item with optional key (defaults to first 32 chars)."""
        storage_key = key or item.metadata.get("key") or item.content[:32]
        self._backend.store(storage_key, item)

    def retrieve(self, query: Optional[str] = None, limit: int = 10) -> List[MemoryItem]:
        """Retrieve items matching query."""
        if not query:
            return list(self._backend.iter_items())
        return self._backend.search(query, limit=limit)

    def get(self, key: str) -> Optional[MemoryItem]:
        """Get item by exact key."""
        return self._backend.get(key)

    def clear(self) -> None:
        self._backend.clear()
```

---

## 5. Retrieval Strategies

### 5.1 Term-Matching Retrieval

The simplest retrieval strategy matches query terms against content:

```python
def retrieve_by_terms(query: str, items: List[MemoryItem]) -> List[Tuple[MemoryItem, float]]:
    """Retrieve items with relevance scores based on term matching."""
    query_terms = set(query.lower().split())
    results = []
    
    for item in items:
        content_terms = set(item.content.lower().split())
        matches = len(query_terms & content_terms)
        
        if matches > 0:
            relevance = matches / len(query_terms)
            results.append((item, relevance))
    
    # Sort by relevance descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results
```

### 5.2 Retrieval Trace Pattern

Always include trace information for debugging:

```python
@dataclass
class RetrievalTrace:
    """Trace information about memory retrieval."""

    query: str
    short_term_items: List[MemoryItem]
    long_term_items: List[MemoryItem]
    retrieval_time_ms: float
    relevance_scores: Dict[str, float] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format trace for display."""
        lines = [
            "\n=== Memory Retrieval Trace ===",
            f"Query: {self.query}",
            f"Retrieval time: {self.retrieval_time_ms:.2f}ms",
            f"\nShort-term: {len(self.short_term_items)} items",
            f"Long-term: {len(self.long_term_items)} items",
        ]
        
        for content, score in self.relevance_scores.items():
            lines.append(f"  - {content[:50]}...: {score:.3f}")
        
        return "\n".join(lines)
```

### 5.3 Retrieval with Confidence Weighting

Combine relevance and confidence for ranking:

```python
def retrieve_with_confidence(
    query: str, 
    agent: MemoryAgent,
    min_confidence: float = 0.5
) -> List[Tuple[MemoryItem, float]]:
    """Retrieve items weighted by both relevance and confidence."""
    
    # Get all facts
    facts = agent.get_all_facts()
    
    # Calculate combined score
    query_terms = set(query.lower().split())
    results = []
    
    for fact in facts:
        if fact.confidence < min_confidence:
            continue  # Skip low-confidence facts
        
        content_terms = set(fact.content.lower().split())
        matches = len(query_terms & content_terms)
        
        if matches > 0:
            relevance = matches / len(query_terms)
            combined_score = relevance * fact.confidence  # Weight by confidence
            
            item = fact.to_memory_item()
            results.append((item, combined_score))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results
```

---

## 6. Multi-Turn Conversation Example

### 6.1 Complete Conversation Flow

Here's a 7-turn conversation demonstrating memory accumulation:

```python
from labs.04.src.memory_agent import MemoryAgent

async def multi_turn_conversation():
    """Demonstrate memory accumulation across turns."""
    agent = MemoryAgent(max_short_term=10)
    
    # Turn 1: Initial context
    agent.add_conversation_turn("user", "I live in Seattle")
    agent.add_fact("User lives in Seattle", confidence=1.0, key="location")
    agent.add_conversation_turn("assistant", 
        "Got it! I'll remember that you live in Seattle.")
    
    # Turn 2: Context retrieval
    agent.add_conversation_turn("user", "What's the weather like here?")
    memories = agent.retrieve("Seattle weather", include_trace=True)
    # Agent uses "Seattle" from memory to answer
    agent.add_conversation_turn("assistant", 
        "Based on your location in Seattle, the weather is...")
    
    # Turn 3: Adding preferences
    agent.add_conversation_turn("user", "I like hiking")
    agent.add_fact("User enjoys hiking", confidence=1.0, key="hobby")
    agent.add_conversation_turn("assistant", 
        "Hiking is a great activity! I'll remember that.")
    
    # Turn 4: Multi-context query
    agent.add_conversation_turn("user", "Recommend weekend activities")
    memories = agent.retrieve("Seattle hiking weekend", include_trace=True)
    # Agent combines location + hobby
    agent.add_conversation_turn("assistant", 
        "For weekend activities in Seattle, considering your love for hiking...")
    
    # Turn 5: Dietary preference
    agent.add_conversation_turn("user", "Remember: I'm vegetarian")
    agent.add_fact("User is vegetarian", confidence=1.0, key="diet")
    agent.add_conversation_turn("assistant", 
        "I've noted that you're vegetarian.")
    
    # Turn 6: Complex recommendation
    agent.add_conversation_turn("user", "Suggest a restaurant")
    memories = agent.retrieve("Seattle vegetarian restaurant", include_trace=True)
    # Agent uses location + diet
    agent.add_conversation_turn("assistant", 
        "For vegetarian options in Seattle, I recommend...")
    
    # Turn 7: Memory introspection
    agent.add_conversation_turn("user", "What do you know about me?")
    facts = agent.get_all_facts()
    summary = "\n".join(f"- {f.content} (confidence: {f.confidence:.2f})" 
                        for f in facts)
    agent.add_conversation_turn("assistant", f"Here's what I know:\n{summary}")
    
    return agent

# Run the conversation
agent = asyncio.run(multi_turn_conversation())
print(agent.get_memory_stats())
```

### 6.2 Memory Statistics Output

```python
stats = agent.get_memory_stats()
# {
#     "short_term_count": 14,
#     "short_term_max": 10,  # 4 items pruned
#     "long_term_count": 3,
#     "short_term_usage": 1.0  # 100% full
# }
```

---

## 7. Persistence and Recovery

### 7.1 JSON Serialization

For simple persistence, use JSON:

```python
class MemoryAgent:
    def save_to_json(self, path: str) -> None:
        """Save memory state to JSON file."""
        state = {
            "short_term": [
                {
                    "content": item.content,
                    "timestamp": item.timestamp.isoformat(),
                    "metadata": item.metadata,
                }
                for item in self.short_term.retrieve()
            ],
            "long_term": [
                fact.to_dict() for fact in self.get_all_facts()
            ],
            "max_short_term": self.max_short_term,
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> MemoryAgent:
        """Load memory state from JSON file."""
        with open(path, "r") as f:
            state = json.load(f)
        
        agent = cls(max_short_term=state.get("max_short_term", 10))
        
        # Restore short-term memory
        for item_data in state.get("short_term", []):
            agent.add_conversation_turn(
                role=item_data["metadata"].get("role", "unknown"),
                content=item_data["content"],
            )
        
        # Restore long-term memory
        for fact_data in state.get("long_term", []):
            agent.add_fact(
                content=fact_data["content"],
                confidence=fact_data.get("confidence", 1.0),
                key=fact_data.get("metadata", {}).get("key"),
            )
        
        return agent
```

### 7.2 Session Recovery Pattern

```python
# Save session on exit
def save_session(agent: MemoryAgent, session_id: str) -> None:
    path = f"sessions/{session_id}.json"
    agent.save_to_json(path)
    print(f"Session saved to {path}")

# Load session on start
def load_session(session_id: str) -> Optional[MemoryAgent]:
    path = f"sessions/{session_id}.json"
    if Path(path).exists():
        return MemoryAgent.load_from_json(path)
    return None

# Usage
session_id = "user_12345"
agent = load_session(session_id) or MemoryAgent(max_short_term=20)

# ... conversation ...

save_session(agent, session_id)
```

---

## 8. Performance Considerations

### 8.1 Benchmarks

| Operation | Target | Actual (20 facts, 10 conversations) |
|-----------|--------|-------------------------------------|
| Retrieval | <100ms | ~0.01ms |
| Storage | <10ms | <1ms |
| Save JSON | <50ms | ~5ms |
| Load JSON | <50ms | ~3ms |

### 8.2 Scaling Recommendations

| Memory Size | Backend | Notes |
|-------------|---------|-------|
| < 1,000 items | InMemory | Fast, no persistence |
| 1,000 - 100,000 | SQLite | Good balance |
| > 100,000 | PostgreSQL/Redis | Need connection pooling |
| Semantic search | Vector DB | Pinecone, Weaviate, etc. |

### 8.3 Vector Retrieval Production Patterns (Metadata + Provenance + Fallbacks)

The RAG tier is only production-grade when retrieval is:

- **scoped** (tenant, ACL, doc type)
- **observable** (provenance and logging)
- **robust** (fallbacks when dependencies degrade)

#### A) Store strong metadata per chunk

Every chunk should carry enough provenance to explain why it was retrieved:

- `doc_id`, `chunk_id`
- `source` (kb, runbook, ticket, repo file)
- `timestamp` / `version`
- `tenant_id` (or workspace/project scope)
- optional: `tags`, `owner`, `sensitivity`

Without provenance, you cannot debug, audit, or evaluate retrieval behavior.

#### B) Retrieval pipeline: filter -> retrieve -> rerank -> pack

A practical default pipeline:

1. Pre-filter by tenant + ACL + doc type
2. Retrieve top-K (vector similarity, keyword, or hybrid)
3. Optionally rerank the top-K (cheap heuristic or model-based reranker)
4. Pack evidence into context with citations

#### C) Hybrid retrieval (keyword + vector)

Vector search is powerful, but keyword search still wins for:

- exact identifiers (ticket IDs, error codes)
- rare terms
- structured names

Hybrid retrieval (keyword + vector + merge/rerank) is common in production systems.

#### D) Fallback modes

External dependencies fail (vector DB, embedder, network). Your agent should have explicit fallback modes:

- vector store down -> keyword-only retrieval
- retrieval too slow -> "no retrieval" mode with clear user messaging
- missing provenance -> drop the chunk (do not inject untrusted content)

### 8.4 Memory Optimization Tips

1. **Summarize before pruning:** Instead of discarding old short-term items, summarize them into a single "context summary" fact.

2. **Index frequently-queried facts:** For large long-term memory, add full-text search indexes.

3. **Batch writes:** Accumulate facts and write in batches rather than individual inserts.

4. **TTL for transient facts:** Some facts expire (e.g., "user is in a hurry today")—add TTL metadata.

---

## 2.4 Write Policy: What Gets to Persist

Memory is only useful if it is reliable. The most common failure mode is storing the wrong thing and then trusting it forever.

Write policy answers: **"What is allowed to enter memory?"** It should include:

- **Source requirements**: only store facts that came from trusted tools or verified outputs.
- **User data boundaries**: do not store secrets or PII unless explicitly approved.
- **Confidence thresholds**: store only when confidence is above a minimum threshold.
- **Expiration rules**: not all facts last forever; set retention windows.

Simple example:

```
Store long-term facts if:
  - source == "tool" OR verified == true
  - confidence >= 0.7
  - content is not secret or PII
Else: keep in short-term only.
```

---

## 2.5 Retrieval Policy: What Gets to Influence Output

Retrieval policy answers: **"What is allowed into context?"** This prevents contamination and keeps responses on-topic.

Key rules:

- Prefer **recent** and **high-confidence** memories.
- Filter out memory with missing sources.
- Do not inject contradictory facts without disambiguation.
- Cap the number of retrieved items to protect token budget.

If you cannot justify why a memory was retrieved, you should not use it.

---

## Implementation Guide (using core modules)

Use these repo assets to make the chapter actionable:

- Memory manager: `src/agent_labs/memory/manager.py`
- Tier types: `src/agent_labs/memory/short_term.py`, `long_term.py`, `rag.py`
- Storage backends: `src/agent_labs/memory/storage.py`
- Lab: `labs/04/README.md`
- Runnable snippet: `curriculum/presentable/02_intermediate/snippets/ch02_memory_manager_tiers.py`

Suggested sequence:

1. Read the chapter and inspect the `MemoryManager.observe()` method.
2. Run Lab 04 and track what goes into each tier.
3. Run the snippet and confirm the tier counts and retrieval behavior.

**Deliverable:** a memory architecture diagram + write/retrieval policy.

---

## Common Pitfalls and How to Avoid Them

1. **Storing raw conversation as "facts":** Treat raw history as short-term, not long-term.
2. **Retrieving too much:** Flooding the prompt reduces quality and increases cost.
3. **Ignoring source quality:** Tool outputs and verified facts are not the same as LLM guesses.
4. **No expiration:** Outdated facts are worse than no facts.

---

## Summary

### Key Takeaways

1. **Three-tier memory architecture** (short-term, long-term, RAG) provides the right trade-offs for different use cases.

2. **Episodic vs. semantic memory** mirrors cognitive science—preserve conversation flow (episodic) while extracting durable facts (semantic).

3. **FIFO pruning** keeps short-term memory bounded; configure `max_items` based on your context window budget.

4. **Retrieval strategies** combine term matching with confidence weighting for relevant results.

5. **Persistence is essential** for cross-session continuity; use JSON for development, SQLite for production.

6. **Trace everything** for debugging—include retrieval time, relevance scores, and source tier in all memory operations.

### What's Next

In Chapter 03, you'll learn about **Context Engineering**—how to pack memory into prompts, manage token budgets, and prevent context overflow.

---

## References

- **Lab 4:** [labs/04/README.md](../../../labs/04/README.md) — Memory Management hands-on exercises
- **Source Code:** [src/agent_labs/memory/](../../../src/agent_labs/memory/) — Core implementation
- **Short-term:** [src/agent_labs/memory/short_term.py](../../../src/agent_labs/memory/short_term.py)
- **Long-term:** [src/agent_labs/memory/long_term.py](../../../src/agent_labs/memory/long_term.py)
- **Storage backends:** [src/agent_labs/memory/storage.py](../../../src/agent_labs/memory/storage.py)

---

## Exercises

Complete these exercises in the workbook to reinforce your learning:

1. **Multi-Turn Conversation Trace:** Run Lab 4's example and annotate which memory tier each retrieval uses.

2. **Custom Fact Extraction:** Implement an LLM-based fact extractor that identifies entities and relationships from conversation history.

3. **Persistence Layer:** Implement a Redis-based storage backend and compare performance with SQLite.

4. **Memory Consolidation:** Build a scheduled job that summarizes old short-term memory into long-term facts.

5. **Confidence Decay:** Implement a mechanism that reduces fact confidence over time unless reinforced by new conversations.

---

[Prev](chapter_01_orchestrator_patterns.md) | [Up](README.md) | [Next](chapter_03_context_engineering.md)
