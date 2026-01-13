# Intermediate Glossary

**Level**: Intermediate
**Scope**: Advanced orchestration, memory, context, observability, integration

---

## Terms

1. **Agent loop**: The observe-plan-act-verify-refine cycle that drives execution. (Related: [Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md))
2. **State machine**: A controlled set of valid transitions between agent phases. (Related: [Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md))
3. **ReAct**: A reasoning-and-acting pattern with explicit thought/action steps. (Related: [Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md))
4. **Verification gate**: A decision point that determines whether to stop or refine. (Related: [Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md))
5. **Retry policy**: Rules for when and how to retry failed actions. (Related: [Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md))
6. **Backoff**: Increasing delay between retries to reduce overload. (Related: [Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md))
7. **Tool contract**: Schema and constraints describing tool inputs/outputs. (Related: [Chapter 6: Integration Patterns](../02_intermediate/chapter_06_integration_patterns.md))
8. **Input validation**: Ensuring tool inputs match expected schema before execution. (Related: [Chapter 6: Integration Patterns](../02_intermediate/chapter_06_integration_patterns.md))
9. **Output validation**: Ensuring tool outputs match expected schema after execution. (Related: [Chapter 6: Integration Patterns](../02_intermediate/chapter_06_integration_patterns.md))
10. **Short-term memory**: Recent conversational state kept in a bounded window. (Related: [Chapter 2: Advanced Memory](../02_intermediate/chapter_02_advanced_memory.md))
11. **Long-term memory**: Durable facts and preferences retained across sessions. (Related: [Chapter 2: Advanced Memory](../02_intermediate/chapter_02_advanced_memory.md))
12. **RAG memory**: External knowledge retrieved on demand for context. (Related: [Chapter 2: Advanced Memory](../02_intermediate/chapter_02_advanced_memory.md))
13. **Write policy**: Rules for what is allowed into memory. (Related: [Chapter 2: Advanced Memory](../02_intermediate/chapter_02_advanced_memory.md))
14. **Retrieval policy**: Rules for what is allowed into context. (Related: [Chapter 2: Advanced Memory](../02_intermediate/chapter_02_advanced_memory.md))
15. **Context packing**: Selecting and ordering context items within a token budget. (Related: [Chapter 3: Context Engineering](../02_intermediate/chapter_03_context_engineering.md))
16. **Token budget**: The allowed size of prompt and response combined. (Related: [Chapter 3: Context Engineering](../02_intermediate/chapter_03_context_engineering.md))
17. **Overflow strategy**: How to handle context that exceeds the budget. (Related: [Chapter 3: Context Engineering](../02_intermediate/chapter_03_context_engineering.md))
18. **Chunking**: Splitting documents into smaller segments for retrieval. (Related: [Chapter 3: Context Engineering](../02_intermediate/chapter_03_context_engineering.md))
19. **Observability**: Logs, traces, and metrics for debugging and monitoring. (Related: [Chapter 4: Observability](../02_intermediate/chapter_04_observability.md))
20. **Structured logging**: Logs emitted as consistent key/value records. (Related: [Chapter 4: Observability](../02_intermediate/chapter_04_observability.md))
21. **Tracing span**: A timed segment representing a step in execution. (Related: [Chapter 4: Observability](../02_intermediate/chapter_04_observability.md))
22. **Metrics collector**: Aggregates counters and latency measures. (Related: [Chapter 4: Observability](../02_intermediate/chapter_04_observability.md))
23. **Context window**: The active slice of conversation history used for the prompt. (Related: [Chapter 3: Context Engineering](../02_intermediate/chapter_03_context_engineering.md))
24. **Slot filling**: Collecting required fields over multiple turns. (Related: [Chapter 5: Multi-Turn Conversations](../02_intermediate/chapter_05_multi_turn_conversations.md))
25. **Circuit breaker**: Stops calling a failing tool until a cooldown passes. (Related: [Chapter 6: Integration Patterns](../02_intermediate/chapter_06_integration_patterns.md))

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] At least 20 terms included
- [ ] Definitions are concise and actionable
- [ ] Terms align with intermediate chapters
- [ ] No non-ASCII characters used

