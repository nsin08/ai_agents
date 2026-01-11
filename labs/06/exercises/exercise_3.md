# Exercise 3: Identify Performance Bottleneck

**Objective:** Use metrics to find slow components and propose optimizations.

## Steps
1. Run a complex query (multi-turn + tool), e.g., `"tool: add 2+3 and summarize"`.
2. Capture metrics and trace (turns, total_time_ms, llm_time, tool_time).
3. Compute % time per component = component_time / total_time.
4. Identify bottleneck (>50% of total).
5. Propose an optimization (caching, batching, parallel tool calls, shorter prompts).

## Deliverable
- Short report: metrics table, % breakdown, identified bottleneck, and optimization proposal.
