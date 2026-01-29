# ADR-0002: Deterministic correctness gates via artifacts

**Date:** 2026-01-25  
**Status:** Accepted

## Context

Agent systems are non-deterministic in real mode due to model and tool variability.
We still need a reliable correctness gate for development and CI.

## Decision

- Introduce two explicit modes:
  - `deterministic`: correctness gate; no network/GPU required.
  - `real`: dev/prod; real providers/tools; evaluated via metrics and stability checks.
- Every run produces a `RunArtifact` bundle in a stable format:
  - config snapshot (no secrets)
  - event log (redacted)
  - result summary
  - optional evaluation scorecards/gates

## Consequences

### Positive
- Reproducible runs for CI and debugging.
- Baseline vs candidate comparisons are standardized.
- Hosted service and CLI can converge on identical outputs.

### Negative / trade-offs
- Requires disciplined schema versioning for artifacts/events.
- Deterministic mode requires mock/replay providers and fixtures.

## Alternatives considered

1. Rely only on real-mode testing  
   - Rejected: too flaky and expensive; cannot be a reliable gate.
2. Store only final outputs, not events/artifacts  
   - Rejected: loses explainability and makes regressions hard to debug.

