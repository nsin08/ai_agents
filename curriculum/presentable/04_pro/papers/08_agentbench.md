# Paper Summary: AgentBench - Evaluating LLMs as Agents

- arXiv: 2308.03688 - https://arxiv.org/abs/2308.03688
- Published: 2023-08-07

## One-paragraph takeaway

AgentBench is a benchmark suite designed to evaluate LLMs in agent-like settings rather than static single-turn tasks. It highlights that agent performance depends not only on language ability but also on planning, tool use, environment interaction, and robustness to feedback loops. For pro-level teams, the main value is the framing: you must evaluate the whole agent loop (tools, retries, memory, policies) because model-only benchmarks will not predict system behavior.

## What the paper contributes (agent-relevant)

- Task types that resemble agent behavior (multi-step, interactive).
- Emphasizes end-to-end evaluation and failure mode analysis.
- Encourages standardized environments for reproducible agent comparisons.

## How to use the idea in your org

1. Create an internal "AgentBench-like" suite.
   - Include tool use, multi-turn workflows, and partial failures.
2. Measure beyond success/failure.
   - tool-call validity, recovery rate, unsafe action blocks, cost per success.
3. Run it continuously.
   - Use CI gates for regressions and weekly scorecards for improvements.

## Failure modes to watch

- Benchmark overfitting: optimizing for the suite instead of user outcomes.
- Unclear scoring: "pass/fail" hides partial success and safety violations.
- LLM-as-judge drift: evaluation changes as models change.

## Evaluation guidance

- Prefer deterministic metrics where possible (schema validity, exact matches).
- When using LLM judges, use multi-judge + calibration sets + spot-checking.

## How it maps to this curriculum

- Chapter 04 uses AgentBench to motivate frontier evaluation and why "system benchmarks" matter.
- The evaluation framework in `../benchmark_evaluation_framework.md` shows how to build a lightweight internal suite.

