# ADR-002: Multi-Agent Orchestration Pattern (Router + Decomposition First)

**Status:** Accepted (curriculum reference)  
**Date:** 2026-01-11  
**Related chapter:** `../chapter_02_multi_agent_systems.md`

## Context

Some workflows exceed the practical limits of a single agent due to:

- context volume
- conflicting skill modes (creative vs strict verification)
- permission boundaries (read vs write)
- need for parallelism

However, multi-agent systems introduce complexity and additional failure modes.

## Decision

Adopt a staged approach:

1. Start with **router + decomposition** patterns (deterministic, testable).
2. Add hierarchical manager patterns only when needed (explicit roles and boundaries).
3. Require traceability and stop conditions in all multi-agent systems.

Capabilities are treated as permissions, with per-agent tool allowlists and guardrail configs.

## Alternatives Considered

1. Swarm/peer collaboration by default
   - Rejected: high cost and complexity without strong verification.
2. Fully LLM-driven routing and decomposition
   - Rejected: hard to test; must be constrained by deterministic rules and schemas.
3. Single agent with ever-larger prompts
   - Rejected: cost and latency scale poorly; safety and debugging suffer.

## Consequences

### Positive

- Clear, teachable progression from simple to advanced coordination
- Deterministic core that is easier to test and debug
- Stronger safety posture through explicit boundaries

### Negative / Costs

- Additional orchestration code and operational burden
- Requires strong observability to debug routing and coordination errors

## Implementation Notes

- Enforce stop conditions: max subtasks, max retries, max time, max tool calls.
- Require evidence-carrying results (answer + citations + tool outputs).

## Links

- Lab 8: `../../../labs/08/README.md`
- Multi-agent system: `../../../labs/08/src/multi_agent_system.py`
- Case study: `../case_studies/02_multi_agent_incident_response.md`

