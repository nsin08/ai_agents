# Level 2 Slides — Core Components & Integration (I1–I7)

Use this as a slide outline. Each “Slide” section is intended to become 1 slide.

---

## Slide — Title

AI Agents: Core Components & Integration (Level 2)

---

## Slide — Level 2 Outcomes

- Orchestrator/controller design (state, retries, stop conditions)
- Tool contracts (schema, RBAC, side effects)
- Memory systems (RAG + write/retrieval policy)
- Context engineering (token budgets + citations)
- Guardrails and observability (production requirements)

---

## Slide — I1: Orchestrator Deep Dive

- LLM proposes; orchestrator enforces
- State machine mindset: transitions, retries, timeouts
- Verification is part of the loop (not optional)

---

## Slide — I2: Multi-Model Routing

- Why multi-LLM: cost + latency + accuracy + risk
- Router → Planner → Executor → Critic pattern
- Risk triggers → stronger model or HITL gate

---

## Slide — I3: Tools as Production APIs

- Tool schema validation and authz are non-negotiable
- Side effects must be explicit (writes, deletes, irreversible)
- Idempotency + rollback are design requirements

---

## Slide — I4: Memory System Architecture

- Session state vs long-term memory vs RAG are different
- Write policy prevents contamination and privacy issues
- Retrieval policy prevents garbage-in-context failures

---

## Slide — I5: Context Engineering

- Context window is scarce compute
- Structure beats raw text dumps
- Token budgets + overflow strategies prevent brittle behavior

---

## Slide — I6: Guardrails

- “Advice” is not safety; enforcement is safety
- Confirmation gates for writes and irreversible actions
- Block prompt injection at tool boundaries

---

## Slide — I7: Observability

- Logs + metrics + traces → debug and improve
- Track cost per task and tool failures
- Safety events are first-class telemetry

---

## Slide — Level 2 Projects

- P03: Support agent (read-only)
- P04: Multi-tool orchestrator
- P05: RAG with evaluation
