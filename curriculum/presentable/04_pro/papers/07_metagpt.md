# Paper Summary: MetaGPT - Meta Programming for a Multi-Agent Collaborative Framework

- arXiv: 2308.00352 - https://arxiv.org/abs/2308.00352
- Published: 2023-08-01

## One-paragraph takeaway

MetaGPT argues that multi-agent systems benefit from "human workflow structure": roles, handoffs, and Standard Operating Procedures (SOPs). Instead of treating multi-agent chat as free-form, MetaGPT encodes a pipeline (an assembly line) where agents produce intermediate artifacts that other agents review. The practical insight for pro-level engineering is that collaboration is not magic; it is process design. Roles, boundaries, and artifact contracts are what reduce cascading hallucinations.

## What the paper contributes (agent-relevant)

- A pattern library for role-based agent collaboration.
- Emphasizes intermediate artifacts (specs, designs, tests) as stabilizers.
- Shows improved coherence vs naive "agents talking to each other" baselines.

## How to apply it without copying the whole framework

1. Define roles as capability boundaries.
   - Example roles: Planner, Researcher, Implementer, Verifier, Approver.
2. Use artifact contracts.
   - Each stage emits a typed artifact (JSON or Markdown with required sections).
3. Add review stages.
   - A verifier agent (or deterministic checks) reviews before advancing.
4. Keep humans in the loop for high stakes.
   - SOPs should include escalation and approval points.

## Failure modes to watch

- Role confusion: agents overlap and repeat work.
- Coordination overhead: too many agents increase latency and cost.
- Shared context bloat: conversation history grows without control.

## Evaluation guidance

- Measure:
  - quality of intermediate artifacts (completeness checks)
  - end-to-end success rate
  - cost per success
  - traceability (can you explain why a decision was made?)

## How it maps to this curriculum

- Chapter 03 builds a practical "manager-worker-verifier" collaboration pattern from MetaGPT.
- Chapter 04 positions multi-agent SOPs as an emerging best practice for complex workflows.

