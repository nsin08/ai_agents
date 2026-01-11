# Lab 4: Memory Management

## Learning Objectives

- Understand Memory Tiers: short-term (conversational), long-term (facts), and RAG (retrieval) memory
- Implement Memory Storage: Store facts and conversational context across multiple turns
- Design Retrieval Strategies: Query memory based on relevance, recency, and importance
- Manage Memory Capacity: Handle short-term overflow with summarization or pruning
- Trace Memory Usage: Observe what memories are retrieved and why they're relevant

## Overview

Memory management is crucial for AI agents to maintain context across multiple conversation turns. This lab implements a three-tier memory system:

1. **Short-term memory**: Bounded conversational history with FIFO (First-In-First-Out) pruning
2. **Long-term memory**: Persistent facts with confidence scores
3. **RAG memory**: (Future) Retrieval-augmented generation with vector embeddings

## Memory System Architecture

```
┌─────────────────────────────────────────┐
│          Memory Agent                    │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │   Short-Term Memory (FIFO)     │     │
│  │   - Conversational context     │     │
│  │   - Max size: configurable     │     │
│  │   - Auto-pruning when full     │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │   Long-Term Memory (Facts)     │     │
│  │   - Persistent facts           │     │
│  │   - Confidence scores (0-1)    │     │
│  │   - Searchable by relevance    │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │   RAG Memory (Future)          │     │
│  │   - Vector embeddings          │     │
│  │   - Semantic search            │     │
│  │   - Document retrieval         │     │
│  └────────────────────────────────┘     │
│                                          │
└─────────────────────────────────────────┘
```

## Lab Structure

```
labs/04/
  README.md                    # This file
  data/
    memory_state.json          # Example persisted memory state
  src/
    memory_agent.py            # Core MemoryAgent implementation
    multi_turn_example.py      # 7-turn conversation demo
  tests/
    test_memory_agent.py       # Comprehensive test suite
  exercises/
    exercise_1.md              # Multi-turn conversation trace
    exercise_2.md              # Add facts to long-term memory
    exercise_3.md              # Custom persistence layer
```

## Quick Start

### Run the Multi-Turn Example

```bash
cd /home/runner/work/ai_agents/ai_agents
PYTHONPATH=. python labs/04/src/multi_turn_example.py
```

### Run Tests

```bash
PYTHONPATH=. python -m pytest labs/04/tests/test_memory_agent.py -v
```

### Run Tests with Coverage

```bash
PYTHONPATH=. python -m pytest labs/04/tests/test_memory_agent.py --cov=labs/04/src --cov-report=term-missing
```

## Multi-Turn Conversation Trace

The example demonstrates memory accumulation across 7 conversation turns:

### Turn 1: Initial Context
```
User: I live in Seattle
Agent: Got it! I'll remember that you live in Seattle.
Memory: 1 fact stored (location)
```

### Turn 2: Context Retrieval
```
User: What's the weather like here?
Agent: Based on your location in Seattle...
Retrieved: "User lives in Seattle" from long-term memory
```

### Turn 3: Adding Preferences
```
User: I like hiking
Agent: Hiking is a great activity! I'll remember that.
Memory: 2 facts stored (location, hobby)
```

### Turn 4: Multi-Context Query
```
User: Recommend weekend activities
Agent: For weekend activities in Seattle, considering your love for hiking...
Retrieved: Location + hobby facts combined
```

### Turn 5: Dietary Preference
```
User: Remember: I'm vegetarian
Agent: I've noted that you're vegetarian.
Memory: 3 facts stored (location, hobby, diet)
```

### Turn 6: Complex Recommendation
```
User: Suggest a restaurant
Agent: For vegetarian options in Seattle...
Retrieved: Location + dietary preference facts
```

### Turn 7: Memory Introspection
```
User: What do you know about me?
Agent: Here's what I know:
  - User lives in Seattle (confidence: 1.00)
  - User enjoys hiking (confidence: 1.00)
  - User is vegetarian (confidence: 1.00)
```

## Usage Examples

### Basic Memory Agent

```python
from memory_agent import MemoryAgent

# Initialize agent with max 10 items in short-term memory
agent = MemoryAgent(max_short_term=10)

# Add conversation turns
agent.add_conversation_turn("user", "Hello")
agent.add_conversation_turn("assistant", "Hi there!")

# Add facts to long-term memory
agent.add_fact("User lives in Seattle", confidence=1.0, key="location")
agent.add_fact("User enjoys hiking", confidence=0.9, key="hobby")

# Retrieve relevant memories
memories = agent.retrieve("Seattle hiking", include_trace=True)

# Get all facts
facts = agent.get_all_facts()
for fact in facts:
    print(f"- {fact.content} (confidence: {fact.confidence:.2f})")
```

### Memory Persistence

```python
# Save memory state
agent.save_to_json("labs/04/data/session_123.json")

# Load memory state
loaded_agent = MemoryAgent.load_from_json("labs/04/data/session_123.json")

# Verify facts were preserved
assert len(loaded_agent.get_all_facts()) == len(agent.get_all_facts())
```

### Memory Statistics

```python
stats = agent.get_memory_stats()
print(f"Short-term: {stats['short_term_count']}/{stats['short_term_max']}")
print(f"Long-term: {stats['long_term_count']} facts")
print(f"Usage: {stats['short_term_usage']:.0%}")
```

## Retrieval Strategy

The MemoryAgent uses a term-matching retrieval strategy:

1. **Query Processing**: Split query into terms (words)
2. **Short-Term Search**: Check each conversation turn for term matches
3. **Long-Term Search**: Check each fact for term matches
4. **Relevance Scoring**: Calculate `matches / total_query_terms`
5. **Trace Output**: Display retrieved items with relevance scores

### Relevance Calculation

```python
query_terms = set(query.lower().split())
content_terms = set(item.content.lower().split())
matches = len(query_terms & content_terms)
relevance_score = matches / len(query_terms)
```

### Example Retrieval

```
Query: "Seattle hiking weather"

Item: "User lives in Seattle"
  - Matches: {"seattle"}
  - Score: 1/3 = 0.333

Item: "User enjoys hiking"
  - Matches: {"hiking"}
  - Score: 1/3 = 0.333

Item: "What's the weather like?"
  - Matches: {"weather"}
  - Score: 1/3 = 0.333
```

## Short-Term Memory (FIFO Pruning)

When short-term memory reaches capacity, the oldest items are automatically removed:

```python
agent = MemoryAgent(max_short_term=3)

agent.add_conversation_turn("user", "Message 0")  # Stored
agent.add_conversation_turn("user", "Message 1")  # Stored
agent.add_conversation_turn("user", "Message 2")  # Stored
agent.add_conversation_turn("user", "Message 3")  # Message 0 pruned
agent.add_conversation_turn("user", "Message 4")  # Message 1 pruned

# Only messages 2, 3, 4 remain
```

## Long-Term Memory (Facts with Confidence)

Facts are stored with confidence scores representing certainty:

```python
# High confidence: directly stated by user
agent.add_fact("User lives in Seattle", confidence=1.0)

# Medium confidence: inferred from context
agent.add_fact("User prefers outdoor activities", confidence=0.7)

# Low confidence: weak signal
agent.add_fact("User might like camping", confidence=0.5)
```

## Performance Characteristics

| Operation | Target | Actual (20 facts, 10 conversations) |
|-----------|--------|-------------------------------------|
| Retrieval | <100ms | ~0.01ms |
| Storage   | <10ms  | <1ms |
| Save JSON | <50ms  | ~5ms |
| Load JSON | <50ms  | ~3ms |

## Progressive Exercises

Complete these exercises to master memory management:

1. **Exercise 1**: Run multi-turn conversation and observe memory growth
2. **Exercise 2**: Add 5 facts to long-term memory and verify retrieval
3. **Exercise 3**: Implement save/load persistence across sessions

## Testing

The test suite includes:

- ✅ Agent initialization with configurable short-term size
- ✅ Short-term memory FIFO pruning behavior
- ✅ Long-term memory fact storage and retrieval
- ✅ Confidence score validation (0.0-1.0)
- ✅ Memory retrieval by relevance
- ✅ Retrieval trace output
- ✅ Retrieval latency (<100ms target)
- ✅ Memory persistence (save/load JSON)
- ✅ Memory statistics calculation
- ✅ Multi-turn conversation integration test

**Test Results**: 24/24 passing (100%)
**Code Coverage**: 98.14% (exceeds 80% requirement)

## API Reference

### MemoryAgent

```python
class MemoryAgent:
    def __init__(self, max_short_term: int = 10) -> None:
        """Initialize memory agent with configurable short-term capacity."""
    
    def add_conversation_turn(self, role: str, content: str) -> None:
        """Add a conversation turn to short-term memory."""
    
    def add_fact(self, content: str, confidence: float = 1.0, key: Optional[str] = None) -> None:
        """Add a fact to long-term memory with confidence score."""
    
    def retrieve(self, query: str, include_trace: bool = False) -> List[MemoryItem]:
        """Retrieve relevant memories based on query."""
    
    def get_all_facts(self) -> List[Fact]:
        """Retrieve all facts from long-term memory."""
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history from short-term memory."""
    
    def save_to_json(self, path: str) -> None:
        """Save memory state to JSON file."""
    
    @classmethod
    def load_from_json(cls, path: str) -> MemoryAgent:
        """Load memory state from JSON file."""
    
    def clear(self) -> None:
        """Clear all memory tiers."""
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
```

### Fact

```python
@dataclass
class Fact:
    content: str
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_memory_item(self) -> MemoryItem:
        """Convert fact to MemoryItem."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize fact to dictionary."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Fact:
        """Deserialize fact from dictionary."""
```

### RetrievalTrace

```python
@dataclass
class RetrievalTrace:
    query: str
    short_term_items: List[MemoryItem]
    long_term_items: List[MemoryItem]
    retrieval_time_ms: float
    relevance_scores: Dict[str, float] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Format trace for display."""
```

## Future Enhancements

- **RAG Integration**: Add vector embeddings and semantic search
- **Memory Summarization**: Automatically summarize old short-term memories
- **Importance Scoring**: Weight facts by importance, not just confidence
- **Forgetting Mechanism**: Decay old facts over time
- **Memory Consolidation**: Merge similar facts
- **Context Windows**: Implement sliding window for recent context

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'src'`, run with PYTHONPATH:

```bash
PYTHONPATH=. python labs/04/src/multi_turn_example.py
```

### Memory Not Persisting

Ensure the data directory exists:

```bash
mkdir -p labs/04/data
```

### Tests Failing

Verify you're running from the repository root:

```bash
cd /home/runner/work/ai_agents/ai_agents
PYTHONPATH=. python -m pytest labs/04/tests/ -v
```

## Additional Resources

- Framework memory module: `src/agent_labs/memory/`
- Lab 1 (RAG Fundamentals): `labs/01/`
- Storage backends: `src/agent_labs/memory/storage.py`

## License

Part of the AI Agents educational curriculum.
