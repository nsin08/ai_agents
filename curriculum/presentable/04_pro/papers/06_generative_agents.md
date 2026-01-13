# Paper Summary: Generative Agents - Interactive Simulacra of Human Behavior

- arXiv: 2304.03442 - https://arxiv.org/abs/2304.03442
- Published: 2023-04-07

## One-paragraph takeaway

Generative Agents proposes an architecture for believable simulated agents that observe, plan, and reflect while interacting with an environment and other agents. While the target domain is social simulation, the architecture is broadly applicable: agents need episodic memory (what happened), semantic memory (what it means), and planning that is grounded in both. For engineering teams, the key contribution is a concrete pattern for long-horizon behavior: summarize, store, retrieve, and plan with time-aware relevance.

## What the paper contributes (agent-relevant)

- A memory architecture that separates raw observations from higher-level reflections.
- Demonstrates how memory retrieval can support coherent multi-day behavior.
- Highlights emergent behavior when agents share an environment and interact.

## How to reuse the ideas in real agent products

1. Model memory as an index, not as a log.
   - Store events and summaries with timestamps and importance scores.
2. Retrieval is the control lever.
   - Tune recency vs relevance vs importance.
   - Keep provenance: what memory items drove a decision?
3. "Reflection" is optional but compression is mandatory.
   - Without compression, long-horizon agents drown in their own history.

## Failure modes to watch

- Memory drift: summaries distort facts over time.
- Contamination: adversarial inputs become stored "memories" and influence future actions.
- Cost explosion: retrieval + summarization becomes the dominant spend.

## Evaluation guidance

- Evaluate long-horizon consistency:
  - factual consistency across time
  - goal persistence (does the agent keep its objectives?)
  - memory grounding (can you trace decisions to retrieved items?)

## How it maps to this curriculum

- Chapter 03 uses this paper to motivate multi-agent coordination and memory design patterns.
- The implementation guide in `../advanced_implementation_guide.md` includes a "provenance-first memory" checklist.

