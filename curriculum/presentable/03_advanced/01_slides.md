# Level 3 Slides — Production Patterns & Safety (A1–A6)

Use this as a slide outline. Each “Slide” section is intended to become 1 slide.

---

## Slide — Title

AI Agents: Production Patterns & Safety (Level 3)

---

## Slide — The Production Reality

- Most production agent code is failures + safety + operations
- “It works on my laptop” is not a reliability strategy
- Evaluation and observability are features, not afterthoughts

---

## Slide — A1: Decision Trees

- Make tradeoffs explicit: cost, latency, accuracy, risk
- Choose orchestration + memory + safety posture intentionally

---

## Slide — A2: Failure Modes

- Tool failures, cascade failures, partial success, non-determinism
- Recovery patterns: retries, timeouts, circuit breakers, compensation
- Degradation modes: read-only fallback, ask-for-clarification

---

## Slide — A3: Testing & Evaluation

- Unit/integration tests (deterministic) vs behavior evals (probabilistic)
- Golden tests + adversarial tests + load tests
- Release gates + regression dashboards

---

## Slide — A4: Security & Compliance

- Threat model: prompt injection, tool misuse, data exfil, memory contamination
- Controls: allowlists, schema validation, RBAC, audit logs, tenant isolation

---

## Slide — A5: Human-in-the-Loop (HITL)

- Design approval workflows for high-risk actions
- Confirm-before-write + supervisor queues + two-person rule
- Auditability and timeboxed approvals

---

## Slide — A6: Scalability & Performance

- Routing, caching, concurrency, backpressure
- Don’t optimize away safety and observability

---

## Slide — Level 3 Projects

- P06: Support agent with writes (with approvals)
- P07: Testing harness (golden + adversarial + regression)
- P11: Cost engineering (instrumentation + optimization)
