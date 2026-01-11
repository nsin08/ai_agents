# Exercise 1: Multi-Turn Conversation Trace

**Objective:** Observe memory growth and retrieval across multiple conversation turns.

## Task

1. Run the multi-turn conversation example
2. Observe how memory accumulates from Turn 1 to Turn 7
3. Note when retrieval traces show relevant memories being found

## Steps

```bash
cd /home/runner/work/ai_agents/ai_agents
PYTHONPATH=. python labs/04/src/multi_turn_example.py
```

## Expected Observations

- Turn 1: First fact stored ("User lives in Seattle")
- Turn 2: Memory retrieval finds location context
- Turn 4: Multiple memories retrieved (location + hobby)
- Turn 6: Multiple contexts combined (location + dietary preference)
- Turn 7: All facts retrieved and displayed

## Questions to Consider

1. How many items are in short-term memory at the end?
2. How many facts are in long-term memory?
3. What happens when short-term memory reaches capacity?
4. Which memories are retrieved for each query?

## Hint

<!-- The trace output shows retrieval time and relevance scores for each query. -->
