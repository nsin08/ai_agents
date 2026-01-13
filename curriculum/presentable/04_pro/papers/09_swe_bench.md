# Paper Summary: SWE-bench - Can Language Models Resolve Real-World GitHub Issues?

- arXiv: 2310.06770 - https://arxiv.org/abs/2310.06770
- Published: 2023-10-10

## One-paragraph takeaway

SWE-bench evaluates models and agents on real software engineering issues from GitHub repositories, where success requires understanding a codebase, making correct edits, and passing tests. This matters for agent builders because it pushes evaluation toward real workflows: repo context, tool use (search, edit, run tests), and correctness defined by executable tests. Even if you are not building a "coding agent", SWE-bench is a strong reminder that the best evaluation harness is one that enforces correctness with real constraints.

## What the paper contributes (agent-relevant)

- A dataset of real issues and repos with verifiable success criteria.
- A shift from "looks correct" to "passes tests".
- Highlights gaps between chat performance and task completion performance.

## How to apply the lessons outside software engineering

1. Prefer executable checks.
   - Use validators, schemas, business rule engines, or simulation tests.
2. Make the environment part of the evaluation.
   - If the agent must call tools, the benchmark must include tool calls.
3. Record traces.
   - Debugging failure requires tool traces and intermediate artifacts.

## Failure modes to watch

- Data leakage: models may have seen repos/issues in training.
- Fragile harnesses: evaluation breaks when dependencies change.
- "Test-only" success: passing tests does not guarantee safe behavior.

## How it maps to this curriculum

- Chapter 04 uses SWE-bench to illustrate the direction of agent evaluation: executable, environment-grounded, and traceable.
- The evaluation framework in `../benchmark_evaluation_framework.md` includes "executable checks first" as a rule.

