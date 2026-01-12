# Case Study 04: Multi-Tenant Support Platform (Scaling and Fairness)

**Related chapter(s):** `../chapter_04_scaling_strategies.md`, `../chapter_06_security_best_practices.md`  
**Primary internal references:** `Agents/12_01_customer_support_agent_architecture.md`, `projects/P08_multi_tenant_platform.md`

## Executive Summary

Multi-tenant agent platforms must scale while preserving isolation and fairness. The biggest practical risks are:

- cross-tenant data leakage (catastrophic)
- noisy-neighbor effects (one tenant consumes shared capacity)
- hidden cost spikes due to retries and prompt growth

This case study presents a scaling plan that is safe-by-design:

- per-tenant quotas and budgets
- tenant-scoped caches and retrieval
- explicit concurrency limits and circuit breakers
- observability by tenant and workflow

## Scenario

The platform supports multiple customer tenants. Each tenant has:

- its own knowledge base (docs and tickets)
- its own policy config (guardrails)
- its own cost budget and SLO expectations

Traffic is spiky: outages and releases create bursts.

## Architecture Overview

```
Tenant Users -> API Gateway
  -> AuthN/AuthZ -> tenant context
  -> Agent runtime (shared)
      -> Retrieval (tenant-scoped)
      -> Tools (tenant-scoped)
      -> Guardrails (tenant config)
      -> Observability (per-tenant metrics)
  -> Storage:
      - audit logs (isolated)
      - memory (scoped)
      - caches (scoped)
```

## Scaling Strategy

### 1) Tenant quotas and budgets

Implement quotas at the gateway and at the runtime:

- QPS limits per tenant
- concurrent request limits per tenant
- cost budget per tenant (tokens/cost)

Without this, a single tenant can trigger a retry storm that degrades everyone.

### 2) Caching (with safe keys)

Cache only safe artifacts:

- retrieval results for read-only workflows
- summaries that do not contain sensitive data

Cache keys must include:

- tenant_id
- role scope (if applicable)
- config version

### 3) Concurrency limits and backpressure

Control fan-out:

- cap concurrent tool calls per request
- cap total in-flight requests per tenant
- degrade gracefully when limits are reached

### 4) Circuit breakers and fallbacks

When a shared dependency degrades:

- open circuit breaker for the affected tool/provider
- route to fallback mode (cached summary, read-only response)
  - make fallback explicit in output
  - record telemetry

## Security and Isolation

Minimum requirements:

- tenant_id included in every tool call and storage access
- strict separation for audit logs (access control + retention)
- no shared caches without tenant-scoped keys

## Observability by Tenant

Metrics to track per tenant:

- success rate
- p95 latency
- guardrail blocks by rule
- cost per success
- cache hit rate

Alerts:

- one tenant exceeding budgets or error rates
- sudden drops in success rate after rollout for a tenant

## Lessons Learned

1. Fairness requires quotas and budgeting, not only scaling replicas.
2. Isolation must be enforced at every boundary (tools, retrieval, caches, logs).
3. Tenant-specific observability is required to debug noisy neighbor issues.

## Suggested Exercises

1. Design a cache key strategy for retrieval results that prevents cross-tenant leakage.
2. Create a dashboard grouped by tenant: success rate, cost per success, p95 latency.
3. Write an ADR documenting multi-tenant scaling and isolation decisions.

