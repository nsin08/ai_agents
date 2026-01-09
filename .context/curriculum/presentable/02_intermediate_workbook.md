# Level 2 Workbook — Core Components & Integration (I1–I7)

**Goal:** Move from “correct mental model” to “buildable system design.”  
**Estimated time:** 4–5 weeks (or 6–10 sessions instructor-led).  
**Prereqs:** Level 1 outcomes (agent definition + architecture pillars).

## Level Outcomes

By the end of Level 2, learners can:

- Design an orchestrator/controller that enforces policy and verification
- Implement tool contracts (schema + permissions + side effects + validation)
- Design memory systems (RAG + short/long-term) with safe write/retrieval policies
- Engineer context for reliability (packing, compression, citations, token budgets)
- Add guardrails and observability required for production debugging

## Deliverables (Evidence)

- A controller spec (states, transitions, retry rules, stop conditions)
- 2–3 tool specifications with schemas + RBAC + side effects
- Memory architecture diagram + write policy + retrieval policy
- Context “packing plan” with token budget and citation strategy
- Observability plan: logs, metrics, traces, dashboards, cost attribution

---

## I1 — The Orchestrator (Control Loop Deep Dive)

**Primary sources:** `../../../Agents/05_01_orchestrator_agent_controller.md`, `../../../Agents/05_00_core_components.md`  
**Timebox:** 90–120 minutes

### Objectives

- Separate “reasoning” (LLM) from “control” (orchestrator)
- Define state, steps, and stop conditions
- Design retries, timeouts, and fallbacks

### Exercises

1. Define your agent’s **state model**:
   - goal, constraints, user context, tool results, intermediate artifacts
2. Define **stop conditions**:
   - success, irrecoverable failure, max steps, max cost, max latency
3. Define a **retry policy**:
   - what to retry, how many times, exponential backoff, circuit breaker

---

## I2 — LLM Selection & Multi-Model Routing

**Primary source:** `../../../Agents/05_02_llms_and_reasoning_modes.md`  
**Timebox:** 90–120 minutes

### Objectives

- Understand why production agents often use multiple models
- Design router/planner/executor/critic patterns
- Balance cost, latency, accuracy, and risk

### Exercises

1. Create a routing table for your workflow:
   - “cheap model” for classification/triage
   - “strong model” for planning/complex reasoning
   - “critic model” (or same model) for verification and safety checks
2. Define “risk triggers” that force a stronger model or a human gate.

---

## I3 — Tools & API Integration

**Primary sources:** `../../../Agents/05_03_tools_and_apis_agent.md`, `../../../Agents/09_02_tool_use_computer_control_autonomous_workflows.md`  
**Timebox:** 120–150 minutes

### Objectives

- Treat tools as production APIs with strict contracts
- Design a tool gateway (validation, authz, auditing)
- Reason about side effects and idempotency

### Exercises

For 2 tools in your workflow:

- Write a tool spec:
  - name, description, input schema, output schema
  - permissions/RBAC
  - side effects (“writes what, where”)
  - idempotency and rollback story
- Define “unsafe parameters” that must be blocked or require confirmation.

---

## I4 — Memory Systems (Short-Term, Long-Term, RAG)

**Primary sources:**

- `../../../Agents/05_04_0_memory_and_rag.md`
- `../../../Agents/05_04_2_memory_write_policy.md`
- `../../../Agents/05_04_3_memory_retrieval_policy.md`

**Timebox:** 120–150 minutes

### Objectives

- Separate short-term state from long-term memory
- Use RAG for grounding and citation
- Define memory write and retrieval policies to avoid contamination

### Exercises

1. Design a 3-layer memory model for your workflow:
   - session state (ephemeral)
   - knowledge base (retrieval)
   - long-term memory (persisted user/tenant/task memory)
2. Draft a write policy:
   - what is allowed to be stored
   - when to store
   - privacy boundaries (tenant/user isolation)
3. Draft a retrieval policy:
   - what sources are allowed
   - ranking strategy and filters
   - token budget rules

---

## I5 — Context Engineering

**Primary source:** `../../../Agents/05_04_1_context_engineering.md`  
**Timebox:** 90–120 minutes

### Objectives

- Treat context window as scarce compute
- Decide what to include, compress, and omit
- Improve reliability with structure and citations

### Exercises

1. Build a “context packing plan”:
   - system instructions, policies, tool schemas
   - retrieved documents (with citations)
   - memory snippets (with provenance)
   - conversation summary
2. Define a token budget per category and a fallback when overflow occurs.

---

## I6 — Policies & Guardrails

**Primary source:** `../../../Agents/05_05_policies_and_guardrails.md`  
**Timebox:** 90–120 minutes

### Objectives

- Implement safety as enforcement, not advice
- Define safety tiers and required gates
- Prevent tool misuse and prompt injection risks

### Exercises

1. Define your safety tier (read-only, limited write, high-stakes).
2. Define enforcement points:
   - before tool execution (schema + RBAC)
   - after tool result (sanity checks)
   - before final response (redaction + policy check)
3. Create a “confirmation gate” policy for irreversible actions.

---

## I7 — Observability (Logging, Metrics, Tracing)

**Primary source:** `../../../Agents/05_06_observability_logging_metrics_tracing.md`  
**Timebox:** 90–120 minutes

### Objectives

- Make agent behavior debuggable and auditable
- Track cost, latency, tool failures, and safety interventions
- Build feedback loops for evaluation and improvement

### Exercises

1. Define a minimal telemetry schema:
   - request_id, user/tenant, workflow_id
   - model calls (name, tokens, latency, cost)
   - tool calls (name, args hash, result status, latency)
   - safety events (blocked/approved actions)
2. Define 5 metrics and 3 alerts you would run in production.

---

## Level 2 Hands-On Projects

Recommended sequence:

1. `projects/P03_support_agent_read_only.md`
2. `projects/P04_multi_tool_orchestrator.md`
3. `projects/P05_rag_with_evaluation.md`

---

## Knowledge Check (10 minutes)

- Explain why tool schemas and RBAC belong in the orchestrator, not in the prompt.
- Describe the difference between RAG and long-term memory and why mixing them is risky.
- Name 3 signals you would use to detect regressions in an agent after a model upgrade.

