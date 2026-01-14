# Intermediate Quick Reference

**Level**: Intermediate
**Purpose**: One-page cheat sheet for core patterns

---

## Orchestrator Essentials

- Loop: Observe -> Plan -> Act -> Verify -> Refine
- Max turns: 3-5 for reliable behavior
- Always log state transitions
- Verification is required to stop

## Memory Essentials

- Short-term: bounded, recent context
- Long-term: durable facts only
- RAG: external retrieval
- Write policy + retrieval policy are mandatory

## Context Engineering

- Define a hard token budget
- Use prompt templates with variable validation
- Prefer structured context to raw dumps
- Use chunking for long documents

## Observability

- Log fields: run_id, state, latency_ms, tokens_used
- Trace each OPRV step
- Metrics: error_rate, p95_latency, tool_failures

## Integration Patterns

- Tool contracts with schemas
- Validate inputs before execution
- Retry with backoff and circuit breaker

## Deployment Checklist (Intermediate)

- [ ] Token budget enforced
- [ ] Tool validation enabled
- [ ] Retry policy set
- [ ] Logs + traces + metrics configured
- [ ] Failure path documented

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Scannable sections with short bullets
- [ ] Includes deployment checklist
- [ ] Uses ASCII only

