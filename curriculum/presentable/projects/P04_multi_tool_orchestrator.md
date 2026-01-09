# P04 — Multi-Tool Orchestrator with Dependencies

## Objective
Chain multiple tools with dependencies and enforce step budgets, retries, and parallel execution where safe.

## Success Criteria
- [ ] Executes a 5-tool dependency graph successfully
- [ ] Handles tool failures gracefully (retries/backoff, circuit breakers)
- [ ] Respects max step budget (<=10)
- [ ] Parallelizes safe steps; benchmarks documented

## Scope
- In: 5 mock tools with dependencies, dependency resolver, retry/backoff, step budget, parallel exec, perf benchmarks
- Out: real external systems, prod deployment, multi-tenant

## Constraints
- Budget: prototype
- Timeline: 2 weeks

## Suggested Approach
1. Define tool graph + dependencies
2. Build dependency resolver + scheduler
3. Add retry/backoff + circuit breakers per tool
4. Enforce step budget + stop conditions
5. Benchmark latency/cost; document results
