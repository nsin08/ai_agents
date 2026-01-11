# Exercise 2: Add Facts to Long-Term Memory

**Objective:** Practice storing and retrieving facts with confidence scores.

## Task

Add 5 facts to long-term memory and verify they can be retrieved by relevance.

## Steps

1. Create a new Python script in `labs/04/exercises/`
2. Initialize a MemoryAgent
3. Add 5 facts about a user with varying confidence scores
4. Retrieve facts based on different queries
5. Print the facts and their confidence scores

## Example Code Template

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from memory_agent import MemoryAgent

# Create agent
agent = MemoryAgent()

# Add 5 facts with confidence scores
agent.add_fact("Your fact here", confidence=1.0, key="fact_1")
# ... add 4 more facts

# Retrieve and display facts
facts = agent.get_all_facts()
for fact in facts:
    print(f"- {fact.content} (confidence: {fact.confidence:.2f})")

# Test retrieval
results = agent.retrieve("your query here", include_trace=True)
```

## Expected Output

- List of 5 facts with confidence scores
- Retrieval trace showing which facts match queries
- Relevance scores for matching facts

## Hint

<!-- Try using different confidence scores (0.5-1.0) to represent uncertainty levels. -->
