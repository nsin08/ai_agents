# Exercise 3: Implement Custom Exit Condition

**Objective:** Create and observe confidence-based early stopping.

## Steps
1. Set `confidence_threshold=0.95` when constructing `OrchestratorAgent`.
2. Run the three sample tasks and log confidence progression at each Verify state.
3. Adjust threshold (e.g., 0.6, 0.8, 0.95) and observe:
   - Whether the agent exits earlier
   - How many turns are used
   - Whether results remain correct

## Deliverable
- Modified orchestrator run(s) with logged confidence values and explanation of how the threshold affected stopping behavior.
