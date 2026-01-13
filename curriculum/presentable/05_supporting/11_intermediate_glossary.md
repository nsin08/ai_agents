# Intermediate Glossary

**Level**: Intermediate
**Scope**: Advanced orchestration, memory, context, observability, integration

---

## Terms

1. **Agent loop**: The observe-plan-act-verify-refine cycle that drives execution.
2. **State machine**: A controlled set of valid transitions between agent phases.
3. **ReAct**: A reasoning-and-acting pattern with explicit thought/action steps.
4. **Verification gate**: A decision point that determines whether to stop or refine.
5. **Retry policy**: Rules for when and how to retry failed actions.
6. **Backoff**: Increasing delay between retries to reduce overload.
7. **Tool contract**: Schema and constraints describing tool inputs/outputs.
8. **Input validation**: Ensuring tool inputs match expected schema before execution.
9. **Output validation**: Ensuring tool outputs match expected schema after execution.
10. **Short-term memory**: Recent conversational state kept in a bounded window.
11. **Long-term memory**: Durable facts and preferences retained across sessions.
12. **RAG memory**: External knowledge retrieved on demand for context.
13. **Write policy**: Rules for what is allowed into memory.
14. **Retrieval policy**: Rules for what is allowed into context.
15. **Context packing**: Selecting and ordering context items within a token budget.
16. **Token budget**: The allowed size of prompt and response combined.
17. **Overflow strategy**: How to handle context that exceeds the budget.
18. **Chunking**: Splitting documents into smaller segments for retrieval.
19. **Observability**: Logs, traces, and metrics for debugging and monitoring.
20. **Structured logging**: Logs emitted as consistent key/value records.
21. **Tracing span**: A timed segment representing a step in execution.
22. **Metrics collector**: Aggregates counters and latency measures.
23. **Context window**: The active slice of conversation history used for the prompt.
24. **Slot filling**: Collecting required fields over multiple turns.
25. **Circuit breaker**: Stops calling a failing tool until a cooldown passes.

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] At least 20 terms included
- [ ] Definitions are concise and actionable
- [ ] Terms align with intermediate chapters
- [ ] No non-ASCII characters used

