# Evaluation Gates (Goldens, Scorecards, CI)

## Why this is required

Production agents change behavior due to:
- model/provider changes
- prompt/template changes
- tool changes
- retrieval/index changes

So evaluation must be:
- runnable locally
- runnable in CI
- able to block regressions ("gate")

## Concepts

### GoldenSuite

A set of cases:
- input
- expected outputs or scoring rules
- tags and metadata

Suites can be:
- deterministic (exact match, schema validators)
- metric-based (similarity, rubric score)

### Scorecard

Aggregated results:
- per-case scores and failures
- suite summary metrics
- diffs vs baseline (candidate vs baseline)

### GateDecision

A pass/fail decision with reasons:
- thresholds met / violated
- regressions detected
- stability criteria (variance bounds)

## Deterministic vs real-mode evaluation

Deterministic gate (v1 correctness):
- mock model provider
- deterministic tools and retrieval fixtures
- exact-match and schema scoring

Real-mode evaluation (informational early):
- real providers/tools
- metric-based scoring and stability reruns
- can become a gate once stable

## CI integration

The CLI should support:
- `agent-core eval --suite <path> --baseline <artifact> --candidate <artifact>`
- `agent-core gate --suite <path> --thresholds <file>`

The output should be machine-readable:
- JSON scorecard + gate decision
- non-zero exit code on gate failure

## Stability testing

When using non-deterministic models:
- rerun N times per case
- compute variance bounds
- gate on stability thresholds where applicable

