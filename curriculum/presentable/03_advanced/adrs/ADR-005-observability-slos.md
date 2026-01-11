# ADR-005: Observability Model and SLOs (Outcomes, Safety, Cost)

**Status:** Accepted (curriculum reference)  
**Date:** 2026-01-11  
**Related chapter:** `../chapter_05_monitoring_alerting.md`

## Context

Agent systems require observability beyond standard service metrics:

- behavior and decision tracing (tools, policies)
- safety events (blocks, redaction)
- cost tracking (tokens and dollars)
- evaluation outcomes (golden sets)

Without these, production incidents are difficult to diagnose and regressions are hard to detect.

## Decision

Adopt an observability model that includes:

- structured logs (stable event names)
- metrics (success rate, latency, tool health, safety blocks, cost per success)
- end-to-end traces (turns, tools, providers)
- audit events for high-risk actions (writes)

Define SLOs based on outcomes, not only uptime:

- success rate on golden set
- safety compliance signals
- cost per success thresholds

## Alternatives Considered

1. Standard service metrics only
   - Rejected: insufficient for agent debugging and policy regressions.
2. Full tracing/logging for all requests
   - Rejected: high cost and privacy risk without sampling.
3. Only manual evaluation
   - Rejected: cannot scale; regressions will ship.

## Consequences

### Positive

- Faster debugging and safer rollouts
- Clear signals for drift (cost, blocks, success rate)
- Compliance support via audit logs

### Negative / Costs

- Additional storage/compute for telemetry
- Privacy and retention management required

## Links

- Lab 6: `../../../labs/06/README.md`
- Case study: `../case_studies/05_cost_spike_post_rollout.md`

