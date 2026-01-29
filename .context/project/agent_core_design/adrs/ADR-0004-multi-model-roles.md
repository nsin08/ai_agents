# ADR-0004: Multi-model roles as a first-class configuration concept

**Date:** 2026-01-25  
**Status:** Accepted

## Context

Production agents often use multiple models:
- cheaper models for routing/classification
- stronger models for planning/tool use
- critics/verifiers for safety and quality

We need a configuration model that supports this without hardcoding behavior per provider.

## Decision

- Define stable model roles (router/planner/actor/critic/summarizer/embedder).
- Configure a `ModelSpec` per role (provider + model + timeouts + secrets env reference).
- Build a `ModelRegistry` that resolves role -> `ModelClient` at runtime.
- Add routing policies later as an extension (candidate sets and selection policies).

## Consequences

### Positive
- Clear separation of responsibilities and budgets per role.
- Swappable providers without changing application code.
- Supports future routing/fallback and eval-gated promotion.

### Negative / trade-offs
- Slightly more config complexity than a single global model setting.

## Alternatives considered

1. Single global model setting  
   - Rejected: insufficient for real production systems and cost control.
2. Hardcode role selection into code (not config)  
   - Rejected: reduces flexibility and makes experimentation and rollout harder.

