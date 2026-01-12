# Paper Summary: Tree of Thoughts - Deliberate Problem Solving with Large Language Models

- arXiv: 2305.10601 - https://arxiv.org/abs/2305.10601
- Published: 2023-05-17

## One-paragraph takeaway

Tree of Thoughts (ToT) frames reasoning as a search problem: generate candidate "thoughts", evaluate them, and expand promising branches. This shifts agent behavior from a single linear chain of steps to a structured exploration of alternatives. For pro-level systems, ToT is less about copying the exact algorithm and more about adopting the mindset: reasoning quality improves when you generate multiple candidates, score them with constraints, and only execute the best safe option.

## What the paper contributes (agent-relevant)

- A general recipe: propose multiple partial solutions, score, and continue.
- Demonstrates that search + evaluation can outperform single-pass CoT on some hard tasks.
- Highlights the importance of a scoring function (heuristics, judges, constraints).

## How to apply ToT in agent architectures

1. Use ToT for high-value or high-risk decisions.
   - Example: selecting an execution plan that triggers tool writes.
2. Keep the search space small and bounded.
   - Branching factor and depth must be budgeted.
3. Separate generation from evaluation.
   - Generation: LLM proposes candidates.
   - Evaluation: deterministic checks first, LLM judges only as a secondary signal.

## Failure modes to watch

- Cost explosion: too many candidates, too deep search.
- Evaluation leakage: the same model generating and judging can reinforce biases.
- "Search without constraints": exploring nonsense branches wastes budget and time.

## Evaluation guidance

- Measure:
  - success rate improvement vs baseline
  - added latency / cost per successful task
  - stability (variance across runs)
- Gate ToT usage behind routing rules (only for tasks that need it).

## How it maps to this curriculum

- Chapter 02 turns ToT into an engineering pattern: candidate generation + scoring + selection.
- The benchmark framework in `../benchmark_evaluation_framework.md` recommends measuring cost per success.

