# SPEC-0003: Evaluation Gates (Goldens + CI)

Status: Draft
Date: 2026-01-28
Related ADRs:
- `.context/sprint/sprint-2026-W05/04_DECISIONS/ADR-0004-evaluation-gates-scope.md`

## Abstract
This spec defines evaluation as code and CI gates for agents. It introduces what evaluation is in agent systems, why it must be a gate (not a report), how we implement deterministic gates in Phase 2, and how we decide when to promote real-mode evaluation into a gate.

## 1. Introduction
### 1.1 What is evaluation in an agent system?
Evaluation is a repeatable process that measures whether the system behaves as intended across:
- model/provider changes
- prompt/template changes
- tool changes
- retrieval/index changes
- memory policy changes

### 1.2 Why evaluation must be a gate
If evaluation results do not block regressions, the system will drift until it fails in production. Retrieval and memory amplify this risk because regressions are often silent ("it still answers, but worse").

## 2. Requirements
### 2.1 Functional
- Define GoldenSuites (test cases) and how to execute them.
- Produce a machine-readable Scorecard.
- Produce a GateDecision that can fail CI.

### 2.2 Non-functional
- Deterministic gate must be stable and low-flake.
- Outputs must be explainable: why did it fail?
- Baselines must be versioned and update-controlled.

## 3. Two evaluation modes

### 3.1 Deterministic evaluation (Phase 2 gate)
Purpose: correctness, regression detection, and confidence in changes.

Characteristics:
- deterministic model provider
- deterministic tools
- deterministic retrieval (deterministic embedder + in-memory vector store)
- stable ordering and stable artifacts

### 3.2 Real-mode evaluation (Phase 2 informational)
Purpose: quality signal without blocking delivery.

Characteristics:
- real providers (Ollama/OpenAI)
- subject to variance
- requires stability strategy (reruns, variance thresholds) before gating

## 4. Data formats

### 4.1 GoldenSuite (YAML/JSON)
Minimum fields:
- suite id/name/version
- cases:
  - input
  - tags
  - expected: schema checks and/or exact-match expectations for deterministic mode
  - optional retrieval/memory fixtures

### 4.2 Scorecard (JSON)
Minimum fields:
- per-case results (pass/fail, metrics, diffs)
- suite-level summary
- artifact pointers (baseline/candidate)

### 4.3 GateDecision (JSON)
Minimum fields:
- pass/fail
- violated thresholds
- list of failing case ids

## 5. CLI integration (Phase 3)
Commands:
- `agent-core eval --suite <path> --config <path> --mode deterministic --json`
- `agent-core gate --suite <path> --baseline <artifact> --candidate <artifact> --json`

Exit codes:
- 0 pass
- 4 gate failed

## 6. Decision Guidance (When to gate)

### Gate deterministic evaluation when
- you can run it in CI quickly and deterministically.
- failures are actionable (it tells you which case and why).

### Do NOT gate real-mode until
- you have stability policy (reruns, variance bounds).
- you have cost budget for CI.
- you have an explicit procedure for baseline updates.

## 7. Validation (What "done" means)
- Deterministic gate runs in CI and blocks regressions.
- Scorecard and GateDecision are stored as artifacts.
- Baselines are versioned and cannot be changed accidentally.

## 8. References
```text
Software regression testing (background)
https://en.wikipedia.org/wiki/Regression_testing

Property-based testing (useful concept for invariant checks)
https://hypothesis.readthedocs.io/
```