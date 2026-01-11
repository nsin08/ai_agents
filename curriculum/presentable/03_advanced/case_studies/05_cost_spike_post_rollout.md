# Case Study 05: Cost Spike After Rollout (Monitoring and Release Gates)

**Related chapter(s):** `../chapter_05_monitoring_alerting.md`, `../chapter_03_production_deployment.md`  
**Primary internal references:** `Agents/05_06_observability_logging_metrics_tracing.md`

## Executive Summary

After a model change (or prompt change), cost can spike even if success rate stays stable. This case study shows how to detect, contain, and prevent cost regressions using:

- cost per success metrics
- gating thresholds in CI/CD
- canary rollouts with timeboxed evaluation

## Scenario

The team rolls out a new model routing rule:

- "use a larger model for complex queries"

After deployment:

- token usage increases by 30%
- p95 latency increases by 20%
- user-visible quality changes are unclear

## Detection Signals

Metrics:

- `tokens_used_total` by model
- `cost_usd_total` by model
- `cost_per_success_usd` by workflow
- `p95_latency_ms`

Alert:

- cost per success increase > 25% after rollout (compared to baseline)

## Containment Actions

1. Roll back the routing rule (or revert to previous model).
2. Reduce maximum context size (temporary) to control token usage.
3. Enable circuit breaker for the expensive path if budgets exceeded.

Containment should be timeboxed and reversible.

## Root Cause Analysis (Typical)

Common causes:

- prompt template grew (added long instructions)
- retrieval returned more chunks
- retry behavior increased (timeouts)
- "complex query" classifier became too sensitive

The fix is rarely "optimize the model". It is usually:

- reduce context
- improve routing rules
- improve caching and fallbacks

## Prevention: Release Gates

Add gates:

- block release if `cost_per_success` exceeds baseline by > N%
- block release if p95 latency exceeds baseline by > M%
- require eval report comparing baseline vs candidate

These gates can be automated:

- run a golden set
- record cost and latency
- compare to stored baseline metrics

## Lessons Learned

1. Cost must be treated as a first-class SLO.
2. Canary rollouts must include cost monitoring, not only error monitoring.
3. Deterministic constraints (context budgets) prevent runaway costs.

## Suggested Exercises

1. Define cost gates for one workflow (thresholds and rollback triggers).
2. Build a small baseline dataset and compare new routing rules.
3. Write an ADR documenting cost SLOs and gating approach.

