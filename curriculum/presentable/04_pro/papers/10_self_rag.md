# Paper Summary: Self-RAG - Learning to Retrieve, Generate, and Critique through Self-Reflection

- arXiv: 2310.11511 - https://arxiv.org/abs/2310.11511
- Published: 2023-10-17

## One-paragraph takeaway

Self-RAG studies a retrieval-augmented generation (RAG) setup where the model learns to decide when to retrieve, how to generate with retrieved evidence, and how to critique its own outputs. The key practical insight is that "retrieve every time" is not optimal; retrieval is a decision that should be routed, budgeted, and evaluated. For agent systems, Self-RAG motivates a disciplined pipeline: retrieval gating, citation requirements, and self-critique that is verified against sources.

## What the paper contributes (agent-relevant)

- Emphasizes retrieval as a controllable step (when/what/how much).
- Uses critique signals to improve grounding and reduce unsupported claims.
- Highlights that RAG systems need evaluation beyond answer quality (citation correctness).

## How to apply in production RAG/agent systems

1. Add retrieval gating.
   - Decide: no-retrieve vs light-retrieve vs deep-retrieve.
2. Require evidence.
   - For knowledge claims, require citations (doc id + span if possible).
3. Critique with constraints.
   - Self-critique is useful only when it checks against sources or rules.

## Failure modes to watch

- Prompt injection via retrieved content.
- Citation laundering: citations exist but do not support the claim.
- Over-retrieval: retrieval dominates latency and cost without improving outcomes.

## Evaluation guidance

- Track:
  - citation precision/recall (do citations support the statements?)
  - retrieval hit rate (how often retrieval mattered)
  - cost per grounded answer

## How it maps to this curriculum

- Chapter 02 uses Self-RAG to motivate critique + verification patterns for knowledge tasks.
- Chapter 04 positions "adaptive retrieval" as a frontier that will become standard practice.

