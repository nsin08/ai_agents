# ADR-0004: Evaluation Gates Scope and Delivery (Phase 2+)

Status: Proposed
Date: 2026-01-28
Owners: Architect/PM

## Context
The gap analysis is correct: evaluation exists but it is not a ship gate. Phase 2+ introduces retrieval and memory; these increase behavioral variance and regression risk.

If we do not deliver a gateable evaluation workflow early, Phase 2 will produce features that cannot be trusted or compared.

## Decision
Deliver evaluation as code in Phase 2 with a strict split:
- Deterministic gate (Phase 2): must exist and must be used in CI.
- Real-mode evaluation (Phase 2): informational only.
- Real-mode gate (Phase 3+): only after stability thresholds and variance strategy are defined.

## Options Considered

1) Deterministic gate first (chosen)
- Pros: reliable CI signal; unblocks safe iteration; enables regression detection early.
- Cons: does not measure real model quality directly.

2) Gate on real models immediately
- Pros: closer to production behavior.
- Cons: flaky gates; cost; noisy signals; will slow dev and create distrust in CI.

## Consequences
- We must invest in fixtures and deterministic embedder/vector store for CI.
- We must define:
  - GoldenSuite format
  - Scorecard format
  - GateDecision thresholds and exit codes
- Retrieval/memory changes must include new or updated goldens.

## Implementation Notes
- Add types: GoldenSuite, Scorecard, GateDecision.
- CLI support (Phase 3): `agent-core eval` and `agent-core gate`.
- Baselines:
  - store as artifacts (versioned) rather than in a database in Phase 2.

## Acceptance Criteria
- CI can run deterministic evaluation and fail builds on regression.
- Output is machine-readable JSON.
- Gate decisions are explainable (which cases failed and why).

## Open Questions
- Who owns the golden datasets (PM vs TL)?
- What is the minimum suite size to prevent "green but useless" gates?