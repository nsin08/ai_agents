# Exercise 3: Custom Persistence Layer

**Objective:** Implement save/load functionality to persist memory across sessions.

## Task

Create a script that:
1. Builds up memory through conversation
2. Saves the memory state to a JSON file
3. Loads the state in a new agent instance
4. Verifies all data was preserved

## Steps

1. Create a new Python script
2. Build up a conversation with facts
3. Save to a JSON file using `agent.save_to_json()`
4. Create a new agent and load using `MemoryAgent.load_from_json()`
5. Verify facts and conversation history match

## Example Code Template

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from memory_agent import MemoryAgent

# Build original agent
agent1 = MemoryAgent(max_short_term=10)
agent1.add_fact("Important fact 1")
agent1.add_conversation_turn("user", "Hello")
# ... add more data

# Save to file
save_path = "labs/04/data/my_memory.json"
agent1.save_to_json(save_path)
print(f"Saved memory to {save_path}")

# Load into new agent
agent2 = MemoryAgent.load_from_json(save_path)
print(f"Loaded memory from {save_path}")

# Verify data matches
print(f"Original facts: {len(agent1.get_all_facts())}")
print(f"Loaded facts: {len(agent2.get_all_facts())}")

# Compare facts
for f1, f2 in zip(agent1.get_all_facts(), agent2.get_all_facts()):
    assert f1.content == f2.content
    assert f1.confidence == f2.confidence
    
print("✓ All facts preserved correctly!")
```

## Expected Output

- Confirmation that memory was saved
- Confirmation that memory was loaded
- Verification that all facts and conversations match

## Challenge Extension

Create a session manager that:
- Generates unique session IDs
- Saves each conversation session separately
- Can list and load previous sessions

## Hint

<!-- The JSON format includes max_short_term, short_term items, and long_term facts. -->
