# Paper Summary: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

- arXiv: 2201.11903 - https://arxiv.org/abs/2201.11903
- Published: 2022-01-28

## One-paragraph takeaway

Chain-of-thought (CoT) prompting improves performance on tasks that require multi-step reasoning by showing the model examples that include intermediate steps, not just final answers. The key practical idea is simple: the model often has latent reasoning capability, but you must elicit it with demonstrations that mirror the reasoning format you want. In agent systems, CoT is a "reasoning interface" that can power planning and decomposition, but it also introduces new risks: verbose, unverifiable reasoning traces, and higher sensitivity to prompt format.

## What the paper contributes (agent-relevant)

- Demonstrates large gains on reasoning tasks (math, symbolic, commonsense) when models are prompted with intermediate steps.
- Shows "scale matters": smaller models benefit less; sufficiently large models show emergent improvements.
- Establishes CoT prompting as a general technique, not tied to a single benchmark.

## How to use it in agent systems (practical)

1. Use CoT-like structure for planning, not for user-visible answers.
   - The plan is an internal artifact that is allowed to be verbose.
   - The final answer should be short and evidence-backed.
2. Separate "reasoning text" from "tool calls" and "final outputs".
   - If your system cannot parse or validate it, do not treat it as a control signal.
3. Add verification loops.
   - CoT improves average performance but can still be confidently wrong.
   - Pair it with deterministic checks (unit tests, schema validation, retrieval citations).

## Failure modes to watch (agent-specific)

- Overfitting to prompt format: small phrasing changes degrade reasoning.
- "Hallucinated certainty": a long chain of steps looks convincing without being correct.
- Token blowup: plans + tool logs + retrieved context exceed budget and destabilize outputs.

## Evaluation guidance

- Benchmark CoT vs non-CoT on your golden set, not on generic demos.
- Track:
  - success rate
  - average tokens per task
  - rate of invalid tool calls / schema violations
  - rate of unverifiable claims in final output

## How it maps to this curriculum

- Chapter 02 uses CoT as the baseline reasoning pattern, then introduces search/verification to reduce brittleness.
- The evaluation framework in `../benchmark_evaluation_framework.md` describes how to measure benefit vs cost.

