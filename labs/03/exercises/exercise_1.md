# Exercise 1: Trace Agent Execution

**Objective:** Understand state transitions and timing by reading logs.

## Steps
1. Run from repo root:
   - `$env:PYTHONPATH='.'; python labs/03/src/orchestrator_agent.py`
2. Capture traces for 3 tasks:
   - Weather: `"What's the weather in Seattle?"`
   - Math: `"What's 15% of $234.50 plus $12 shipping?"`
   - Missing tool: `"Send email to user@example.com"`
3. Record for each task:
   - Number of turns
   - State transitions (Observe → Plan → Act → Verify → Refine)
   - Duration per state (target: <500ms per turn)
   - Exit condition (success vs max_turns)

## Deliverable
- Annotated trace showing state machine flow for all 3 tasks.
