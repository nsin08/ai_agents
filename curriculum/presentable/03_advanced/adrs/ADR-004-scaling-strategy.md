# ADR-004: Scaling Strategy (Measure First, Then Cache/Async with Backpressure)

**Status:** Accepted (curriculum reference)  
**Date:** 2026-01-11  
**Related chapter:** `../chapter_04_scaling_strategies.md`

## Context

Agent performance and cost are dominated by:

- LLM calls (token usage)
- slow tools and external dependencies
- retries and tail latency

Naively adding replicas without controlling fan-out and retries can make incidents worse.

## Decision

Adopt a scaling approach that prioritizes:

1. Instrumentation and bottleneck identification (latency/cost by step)
2. Safe caching for read-only artifacts (scoped keys)
3. Async execution only with explicit backpressure (concurrency limits, timeouts)
4. Routing and quotas for multi-tenant fairness

## Alternatives Considered

1. Scale replicas first, then optimize later
   - Rejected: hides root causes and amplifies retry storms.
2. Aggressive caching without scoping
   - Rejected: risks cross-tenant leakage and stale correctness.
3. Async fan-out without concurrency limits
   - Rejected: melts dependencies under load.

## Consequences

### Positive

- Predictable scaling behavior
- Lower cost per success through controlled caching and context limits
- Better incident containment through backpressure

### Negative / Costs

- Requires engineering effort for instrumentation and caching keys
- Requires operational discipline (quotas, budgets, tuning)

## Links

- Case study: `../case_studies/04_multi_tenant_support_platform_scaling.md`

