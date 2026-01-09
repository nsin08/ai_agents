[Previous](09_03_retrieval_tools_planning_modern_stack.md) | [Next](09_05_case_study_engineering_pcb_assistant.md)

# Case Study: Customer Support Agent  

## Table of Contents

- [**Case Study — Customer Support Agent (End-to-End Architecture Mapping)**](#case-study-customer-support-agent-end-to-end-architecture-mapping)
- [1. Use case overview](#1-use-case-overview)
  - [What the agent should handle](#what-the-agent-should-handle)
  - [What the agent must NOT do by default](#what-the-agent-must-not-do-by-default)
- [2. System actors and data sources](#2-system-actors-and-data-sources)
  - [Actors](#actors)
  - [Data sources](#data-sources)
- [3. Architecture (mapped to core components)](#3-architecture-mapped-to-core-components)
  - [3.1 High-level runtime flow](#31-high-level-runtime-flow)
  - [3.2 LLM roles (multi-LLM, production-friendly)](#32-llm-roles-multi-llm-production-friendly)
- [4. Tool layer (APIs the agent can use)](#4-tool-layer-apis-the-agent-can-use)
  - [4.1 Example tools (read-only + write)](#41-example-tools-read-only-write)
  - [4.2 Tool schemas (illustrative)](#42-tool-schemas-illustrative)
- [5. Memory and retrieval design](#5-memory-and-retrieval-design)
  - [5.1 Session memory (ephemeral)](#51-session-memory-ephemeral)
  - [5.2 Long-term memory (selective)](#52-long-term-memory-selective)
  - [5.3 RAG (policy grounding)](#53-rag-policy-grounding)
- [6. Policies, guardrails, and safety tier](#6-policies-guardrails-and-safety-tier)
- [7. Mapping design decisions to the decision tree](#7-mapping-design-decisions-to-the-decision-tree)
  - [Single vs multi-LLM](#single-vs-multi-llm)
  - [RAG vs long context](#rag-vs-long-context)
  - [Autonomy](#autonomy)
  - [Memory strategy](#memory-strategy)
  - [Safety level](#safety-level)
- [8. Example end-to-end workflow (with Plan → Verify → Refine)](#8-example-end-to-end-workflow-with-plan-verify-refine)
  - [User request](#user-request)
  - [8.1 Router classification](#81-router-classification)
  - [8.2 Planner output (structured plan)](#82-planner-output-structured-plan)
  - [8.3 Verification gates](#83-verification-gates)
  - [8.4 Final response composition](#84-final-response-composition)
- [9. Failure scenarios and refinements](#9-failure-scenarios-and-refinements)
  - [Case A: Order ID not found](#case-a-order-id-not-found)
  - [Case B: Refund service timeout](#case-b-refund-service-timeout)
  - [Case C: Policy ambiguity](#case-c-policy-ambiguity)
- [10. Observability and KPIs for this case](#10-observability-and-kpis-for-this-case)
  - [What to trace](#what-to-trace)
  - [Outcome KPIs](#outcome-kpis)
- [11. Scalability tactics specific to support workloads](#11-scalability-tactics-specific-to-support-workloads)
- [12. Summary](#12-summary)


## **Case Study — Customer Support Agent (End-to-End Architecture Mapping)**

This case study shows how the components and design decisions from earlier chapters map to a real, production-grade system: a **Customer Support Agent** that can answer questions, fetch authoritative status, and (when allowed) take bounded actions.

---

## 1. Use case overview

### What the agent should handle
- **Order status**: “Where is my order?”
- **Refund status**: “Is my refund processed?”
- **Policy questions**: “What’s the refund policy for electronics?”
- **Ticketing**: “Open a support ticket with details.”
- **Escalations**: “This is urgent / chargeback risk.”

### What the agent must NOT do by default
- execute irreversible actions without confirmation
- access data outside the user’s scope
- leak PII or internal notes

---

## 2. System actors and data sources

### Actors
- **Customer** (end user)
- **Support agent** (human fallback / escalation)
- **Systems of record**:
  - Orders service
  - Payments/refunds service
  - Ticketing system (e.g., Zendesk/ServiceNow)
  - Knowledge base (policy docs)

### Data sources
- **Structured**: orders DB, refund events, shipment tracking
- **Unstructured**: policy pages, internal runbooks, FAQ, product constraints

---

## 3. Architecture (mapped to core components)

### 3.1 High-level runtime flow

```text
Customer UI
  → API Gateway (auth + rate limits)
    → Orchestrator (Plan → Verify → Refine)
      → Model Router (choose model/mode)
      → RAG Service (policy evidence)
      → Tool Gateway (orders/refunds/ticket tools)
      → Verifier (schemas + policy + evidence)
      → State Store (session)
      → Observability (logs/metrics/traces)
```

### 3.2 LLM roles (multi-LLM, production-friendly)
- **Router model**: classify intent (policy Q vs account lookup vs complaint)
- **Planner model**: create structured plan with constraints
- **Executor model**: produce tool call arguments, interpret tool outputs
- **Verifier (rules first)**: schema + policy + invariants; optional critic model for final quality checks
- **Finalizer model**: user-friendly answer, tone, and formatting

---

## 4. Tool layer (APIs the agent can use)

### 4.1 Example tools (read-only + write)

**Read-only tools**
- `get_order(order_id)`
- `get_shipment_tracking(order_id)`
- `get_refund_status(payment_id)`
- `list_recent_orders(user_id, limit)`

**Write tools (gated)**
- `create_support_ticket(payload)`
- `request_refund(order_id, reason)` *(requires confirmation + policy checks)*

### 4.2 Tool schemas (illustrative)

```json
{
  "name": "get_order",
  "input_schema": {"order_id": "string"},
  "output_schema": {
    "order_id": "string",
    "user_id": "string",
    "status": "string",
    "items": "array",
    "payment_id": "string",
    "created_at": "string"
  }
}
```

Tool gateway responsibilities:
- schema validation
- RBAC/ABAC enforcement
- rate limiting and retries
- redaction of sensitive fields before passing to models

---

## 5. Memory and retrieval design

### 5.1 Session memory (ephemeral)
- current conversation summary
- last tool outputs (or references)
- active plan + step index

### 5.2 Long-term memory (selective)
Store only stable, useful facts:
- preferred contact channel
- language preference
- prior escalations (high-level flags)

Avoid storing:
- full payment info
- addresses
- raw transcripts unless explicitly required and governed

### 5.3 RAG (policy grounding)
- Refund policy
- Return windows by product category
- Exceptions (digital goods, perishable items)
- Shipping SLAs

Retrieval is filtered by:
- region
- product category
- policy version/recency

---

## 6. Policies, guardrails, and safety tier

Recommended safety tier for this case:

- **Tier 1 (read-only)** for most traffic
- **Tier 2 (limited write)** for ticket creation and refund requests with confirmation

Key guardrails:
- **Read-only default** unless user explicitly requests a write action
- **Confirmation gate** for any state-changing action
- **Hard limits**: max steps, max tool calls, max retries, cost budget
- **PII redaction** in logs and LLM-visible tool outputs
- **Scope enforcement**: user can only access their own orders

---

## 7. Mapping design decisions to the decision tree

### Single vs multi-LLM
- Use **multi-LLM**: volume is high and requests vary widely (policy Q → account lookup → escalations).

### RAG vs long context
- Use **RAG** for policy and knowledge grounding.
- Use long context only for “one big document” scenarios (rare for customer support).

### Autonomy
- **Autonomy Tier B/C**:
  - B: read-only tools run autonomously
  - C: writes require user confirmation + policy checks

### Memory strategy
- Ephemeral session memory always
- Long-term memory only for preferences and safety flags

### Safety level
- Tier 1 for informational + account lookups
- Tier 2 for ticket creation/refund requests

---

## 8. Example end-to-end workflow (with Plan → Verify → Refine)

### User request
“Where is my refund for order #A123?”

### 8.1 Router classification
- intent: refund_status
- needs tools: yes
- safety tier: Tier 1 (read-only)

### 8.2 Planner output (structured plan)

```json
{
  "goal": "Return refund status for order A123",
  "constraints": {"mode": "read_only", "max_steps": 6, "max_tool_calls": 3},
  "steps": [
    {"id": 1, "action": "tool", "name": "get_order", "args": {"order_id": "A123"}},
    {"id": 2, "action": "tool", "name": "get_refund_status", "args": {"payment_id": "${from_step_1.payment_id}"}},
    {"id": 3, "action": "retrieve", "name": "rag_search", "args": {"query": "refund processing timelines", "filters": {"region": "${user.region}"}}},
    {"id": 4, "action": "verify", "checks": ["schema", "scope", "evidence" ]},
    {"id": 5, "action": "respond"}
  ]
}
```

### 8.3 Verification gates
- **Scope check**: order.user_id == requester.user_id
- **Schema check**: tool outputs conform
- **Evidence check**: policy snippet for timeline exists OR agent states uncertainty

### 8.4 Final response composition
- Refund status from tool (authoritative)
- Timeline guidance from retrieved policy
- If delayed: next steps + offer to create a ticket

---

## 9. Failure scenarios and refinements

### Case A: Order ID not found
- verification fails → refine
- ask user to confirm order id or show recent orders (`list_recent_orders`)

### Case B: Refund service timeout
- retry with bounded backoff
- if still failing: return partial status + create ticket option

### Case C: Policy ambiguity
- retrieve category-specific policy
- if still ambiguous: state uncertainty and escalate to human queue

---

## 10. Observability and KPIs for this case

### What to trace
- model routing decisions
- tool calls and latencies
- stop reasons (success, needs_user, tool_unavailable)
- cost per request

### Outcome KPIs
- resolution rate without human escalation
- ticket creation rate (good for fallbacks)
- customer satisfaction (CSAT) proxy
- average time-to-resolution
- cost per resolved case

---

## 11. Scalability tactics specific to support workloads

- Cache policy RAG results (scoped by region + version)
- Cache stable read-only tool lookups (short TTL)
- Aggressive routing: small model for FAQs, large only for escalations
- Parallelize independent tool calls when possible
- Rate limit per user to prevent abuse

---

## 12. Summary

This case study demonstrates how the architecture translates into a real product:
- the **orchestrator** controls the loop
- **tools** provide authoritative truth
- **RAG** grounds policy answers
- **guardrails** prevent unsafe actions
- **observability** makes the system debuggable and governable

Next: **10_conclusion_future_directions.md**

[Previous](09_03_retrieval_tools_planning_modern_stack.md) | [Next](09_05_case_study_engineering_pcb_assistant.md)
