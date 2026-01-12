# Benchmark and Evaluation Framework (Pro Level)

This document describes a practical evaluation framework for agent systems.

The main idea:
- Evaluate the whole loop (reasoning + tools + memory + policies), not just the model.
- Prefer executable, deterministic checks where possible.
- Treat evaluation as an always-on control plane (CI gates + ongoing scorecards).

## What to measure (a minimal metric set)

Pick 6-10 metrics you can actually track:
- Task success rate (overall and by intent)
- Invalid tool call rate (schema violations, tool not found)
- Recovery rate after tool failures (did retries/fallbacks work?)
- Unsafe action blocked count (guardrails firing is a signal, not a failure)
- Citation precision (for RAG/knowledge tasks)
- P95 latency
- Cost per successful task
- Stability (variance across repeated runs)

## Benchmark types (recommended layers)

1. Tool contract tests (deterministic)
   - validates schema, permissions, error handling
2. Orchestrator/state tests (deterministic)
   - validates state transitions, stop conditions, retry logic
3. Golden behavior set (semi-deterministic)
   - fixed scenarios with expected outputs or checks
4. Adversarial set (semi-deterministic)
   - prompt injection, jailbreak attempts, unsafe args, malformed inputs
5. System canaries (online)
   - small set run in production to detect drift

## A lightweight harness in this repo (agent_labs.evaluation)

This repo provides a small evaluation module:
- `src/agent_labs/evaluation/runner.py` - batch runner
- `src/agent_labs/evaluation/scorers.py` - basic scorers

Example: run an offline benchmark with a simple scorer.

```python
from agent_labs.evaluation.runner import BenchmarkCase, BenchmarkRunner
from agent_labs.evaluation.scorers import SimilarityScorer

cases = [
    BenchmarkCase(case_id="c1", input_text="Capital of France?", reference="Paris"),
    BenchmarkCase(case_id="c2", input_text="2 + 2?", reference="4"),
]

outputs = {
    "c1": "Paris",
    "c2": "4",
}

runner = BenchmarkRunner(metric=SimilarityScorer())
result = runner.run(cases=cases, outputs=outputs)
for row in result.cases:
    print(row["case_id"], row["score"], row["explanation"])
```

Note: For pro use, you should extend this with:
- tool-call validity metrics
- citation checks for RAG tasks
- safety policy checks
- cost/latency collection

## Scoring guidelines (avoid common traps)

### Prefer deterministic scoring

When you can, define correctness as:
- "passes validation"
- "matches expected output"
- "passes simulation"
- "writes the correct diff"

This is why SWE-bench is influential: it defines success via tests.

### When using LLM-as-judge

If you must use a judge model:
- keep judge prompts stable and versioned
- use multiple judges (or repeated judging) to reduce variance
- calibrate with a small human-labeled set
- never let "judge score" be the only release gate for high-stakes workflows

## Suggested benchmark suite for the Pro curriculum

Build a suite that matches the 4 Pro chapters:

Chapter 01 (frameworks):
- state transition correctness
- interrupt/approval enforcement

Chapter 02 (reasoning):
- candidate selection improves success rate on hard tasks
- verification catches unsupported claims

Chapter 03 (patterns):
- tool schema validity and error recovery
- multi-agent verifier catches invalid plans

Chapter 04 (frontiers):
- benchmark coverage (new task types)
- drift detection (weekly scorecards)

## Evidence you should capture in PRs

For production-oriented changes, include:
- benchmark summary table
- list of failures and how they were fixed
- cost/latency deltas on a fixed suite
- traces for at least 1 success and 1 failure case

