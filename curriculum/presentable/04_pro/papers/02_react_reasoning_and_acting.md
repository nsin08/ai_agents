# Paper Summary: ReAct - Synergizing Reasoning and Acting in Language Models

- arXiv: 2210.03629 - https://arxiv.org/abs/2210.03629
- Published: 2022-10-06

## One-paragraph takeaway

ReAct interleaves reasoning steps ("thought") with actions ("act") so the model can use tools or external environments while it reasons. This reduces hallucination (because the agent can fetch facts) and improves interpretability (because actions are visible). For production agent systems, the lasting impact is the separation of concerns: the model proposes actions, but the runtime enforces tool contracts, permissions, and verification before executing anything.

## What the paper contributes (agent-relevant)

- A simple interaction format that combines planning and execution in a loop.
- Evidence that "act + observe" can reduce hallucination and error propagation vs pure CoT.
- Demonstrates improvements on QA and decision tasks when the agent can consult external sources.

## How to use it in real systems (practical)

1. Treat "actions" as typed tool calls, not free-text.
   - Parse tool name + arguments.
   - Reject anything that does not validate against a schema.
2. Log and replay.
   - ReAct-style loops are only debuggable if you capture the action trace and observations.
3. Bound the loop.
   - Enforce max steps, timeouts, and cost budgets.
   - Add an explicit stop condition (done/failed/escalate).

## Failure modes to watch

- Tool hallucination: model calls tools that do not exist.
- Over-acting: agent spams tools instead of reasoning, increasing cost/latency.
- Untrusted observations: retrieval/tool output can contain prompt injection; do not feed it back unfiltered.

## Evaluation guidance

- Evaluate "tool use correctness", not just answer quality:
  - correct tool selection rate
  - argument validity rate
  - recovery rate after tool failure
  - citations grounded in retrieved content

## How it maps to this curriculum

- Chapter 01 uses ReAct as the conceptual backbone for building state-machine workflows (graph or loop).
- Chapter 03 uses ReAct traces as the raw material for observability and debugging patterns.

