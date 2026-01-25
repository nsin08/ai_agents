# ADR-0010: Evaluation gates are first-class primitives

**Date:** 2026-01-25  
**Status:** Accepted

## Context

Without evaluation gates, agent changes can regress silently.
We need a repeatable mechanism to compare baseline vs candidate behavior and block regressions.

## Decision

- Implement evaluation primitives in core:
  - `GoldenSuite` (cases)
  - `Scorer` (metrics and validators)
  - `Scorecard` (aggregated results)
  - `GateDecision` (pass/fail)
- CLI supports `eval` and `gate` commands that:
  - produce machine-readable outputs
  - fail with non-zero exit codes on gate failure

## Consequences

### Positive
- Repeatable shipping discipline.
- Enables CI to enforce quality.
- Supports gradual model/provider changes via baseline comparisons.

### Negative / trade-offs
- Requires ongoing maintenance of golden suites and thresholds.

## Alternatives considered

1. Rely on manual QA only  
   - Rejected: too slow and error-prone for fast iteration.

