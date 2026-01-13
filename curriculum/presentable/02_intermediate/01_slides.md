# Level 2 Slides — Intermediate Curriculum

Use this as a slide outline. Each `## Slide` section is intended to become 1 slide.

---

## Slide — Title

AI Agents (Level 2): Intermediate — Core Components & Production Patterns

---

## Slide — Who This Is For

- You’ve built a basic agent (LLM + tools + memory)
- You want production-grade patterns: reliability, observability, integration
- You can read Python async/await and understand basic APIs

---

## Slide — Level 2 Outcomes

- Implement an orchestration loop with retries + verification
- Design multi-tier memory (short / long / RAG) with policies
- Engineer context for token budgets and overflow control
- Add logs, traces, and metrics for debugging + cost visibility
- Build resilient integrations (auth, timeouts, retry, circuit breaker)

---

## Slide — Curriculum Map (6 Chapters)

1. Orchestrator patterns
2. Advanced memory
3. Context engineering
4. Observability
5. Multi-turn conversations
6. Integration patterns

---

## Slide — The Core Loop (OPRV)

Observe → Plan → Act → Verify → Refine

- The LLM proposes; the orchestrator enforces
- Verification is part of the loop (not optional)
- Refinement is controlled, not “just ask again”

---

## Slide — Chapter 1: Orchestrator Patterns

- State machines and valid transitions
- Planning errors vs action errors vs verification errors
- Stop conditions: max turns, max cost, max latency

Lab mapping: `labs/03/README.md`

---

## Slide — Memory Is Not One Thing

Three distinct tiers:

- Short-term: recent conversational state
- Long-term: durable facts/preferences
- RAG: external knowledge retrieval

---

## Slide — Chapter 2: Advanced Memory

- Write policies (what is allowed to be persisted)
- Retrieval policies (what is allowed into context)
- “Contamination” risks and how to prevent them

Lab mapping: `labs/04/README.md`

---

## Slide — Context Is Scarce Compute

Context window is a constrained budget:

- Prefer structure over dumping raw text
- Enforce token budgets (hard + soft limits)
- Use overflow strategies (truncate, summarize, retrieve)

---

## Slide — Chapter 3: Context Engineering

- Prompt templates + variables
- Token estimation and packing
- Chunking strategies for retrieval

Lab mapping: `labs/05/README.md`

---

## Slide — Observability: Debugging Is a Feature

If you can’t answer “why did it do that?”, it’s not production-ready.

- Logs: structured events with context
- Traces: step-level timing + causality
- Metrics: counters + latency distributions

---

## Slide — Chapter 4: Observability

- Structured logging (JSON)
- Tracing spans across OPRV steps
- Metrics: latency, token usage, tool calls, error rates

Lab mapping: `labs/06/README.md`

---

## Slide — Multi-Turn Conversation Design

- Session state ≠ long-term memory
- Repair strategies for partial/incorrect user input
- Slot filling and “known/unknown” tracking

---

## Slide — Chapter 5: Multi-Turn Conversations

- Conversation state model
- History windowing vs summarization
- Safe memory write-back rules

---

## Slide — Integration Patterns: From Demos to Systems

- Tools are production APIs with contracts
- Validate inputs before execution; validate outputs after
- Reliability patterns: timeouts, retry, circuit breakers

---

## Slide — Chapter 6: Integration Patterns

- Tool contracts: name, description, schemas, constraints
- Tool discovery and execution (registry)
- Error handling: missing tools, validation errors, failures

---

## Slide — Verified Examples

Runnable intermediate snippets live here:

- `curriculum/presentable/02_intermediate/snippets/README.md`

They are exercised by:

- `tests/integration/test_intermediate_snippets.py`

---

## Slide — Close: What “Good” Looks Like

- Deterministic behavior under failure (retries, timeouts, fallbacks)
- Measurable behavior (logs, traces, metrics)
- Safe behavior (policies and guardrails)
- Testable behavior (mockable providers/tools; runnable examples)

