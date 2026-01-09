[Previous](09_05_case_study_engineering_pcb_assistant.md) | [Next](10_conclusion_future_directions.md)

# Architecture Decisions Mapped to Systems  

## Table of Contents

- [**How Architecture + Decisions Map to a Real Agent System**](#how-architecture-decisions-map-to-a-real-agent-system)
- [1. Start with requirements (what success means)](#1-start-with-requirements-what-success-means)
  - [1.1 Functional requirements](#11-functional-requirements)
  - [1.2 Non-functional requirements](#12-non-functional-requirements)
  - [1.3 Safety requirements](#13-safety-requirements)
- [2. Map requirements to the core components](#2-map-requirements-to-the-core-components)
  - [2.1 Mapping table (use this as a checklist)](#21-mapping-table-use-this-as-a-checklist)
- [3. Apply the decision tree (make choices explicit)](#3-apply-the-decision-tree-make-choices-explicit)
  - [3.1 Single vs multi-LLM](#31-single-vs-multi-llm)
  - [3.2 RAG vs long context](#32-rag-vs-long-context)
  - [3.3 Autonomy tier](#33-autonomy-tier)
  - [3.4 Tools vs internal code](#34-tools-vs-internal-code)
  - [3.5 Memory type](#35-memory-type)
  - [3.6 Safety level](#36-safety-level)
- [4. Convert decisions into an implementation blueprint](#4-convert-decisions-into-an-implementation-blueprint)
  - [4.1 Tool inventory](#41-tool-inventory)
  - [4.2 Orchestrator state machine](#42-orchestrator-state-machine)
  - [4.3 Evidence policy](#43-evidence-policy)
  - [4.4 Write-action policy](#44-write-action-policy)
- [5. Reference runtime architecture](#5-reference-runtime-architecture)
- [6. How this mapping appears in the two case studies](#6-how-this-mapping-appears-in-the-two-case-studies)
  - [6.1 Customer Support Agent (example mapping)](#61-customer-support-agent-example-mapping)
  - [6.2 Engineering/PCB Assistant (example mapping)](#62-engineeringpcb-assistant-example-mapping)
- [7. Operationalization checklist](#7-operationalization-checklist)
  - [Build](#build)
  - [Test](#test)
  - [Deploy](#deploy)
- [8. Summary](#8-summary)


## **How Architecture + Decisions Map to a Real Agent System**

This document is a reusable bridge between the **theory (architecture + decision tree)** and a **real implementation**. It shows how to translate requirements into concrete choices about models, tools, memory, safety, and operations.

Use it as a template for any agent — including:
- **Customer Support Agent** (`09_04_case_study_customer_support_agent.md`)
- **Engineering/PCB Assistant** (`09_05_case_study_engineering_pcb_assistant.md`)

---

## 1. Start with requirements (what success means)

Capture requirements in a structured way.

### 1.1 Functional requirements
- user intents (top 10)
- must-call systems of record
- allowed actions (read vs write)
- required outputs (report, ticket, diff, deployment, etc.)

### 1.2 Non-functional requirements
- latency SLOs (p95/p99)
- reliability targets
- cost per request
- compliance constraints (PII/IP)
- auditability requirements

### 1.3 Safety requirements
- what could go wrong?
- what must require approval?
- what must be blocked?

---

## 2. Map requirements to the core components

### 2.1 Mapping table (use this as a checklist)

| Requirement | Component(s) | Design choice | Why |
|---|---|---|---|
| Needs authoritative status | Tools/APIs | Read-only tools + caching | eliminates hallucinations |
| Needs policy answers | RAG | vector + metadata filters + rerank | grounding + precision |
| Needs multi-step workflow | Orchestrator | Plan→Verify→Refine loop | reliability |
| Needs safe writes | Guardrails | approval gates + idempotency | prevents damage |
| Needs repeat context | Memory | session state + selective long-term | continuity |
| Needs debugging | Observability | traces + tool logs + cost | production ops |

---

## 3. Apply the decision tree (make choices explicit)

### 3.1 Single vs multi-LLM
Choose multi-LLM when:
- queries vary widely in complexity
- structured tool use is heavy
- verification matters

Choose single-LLM when:
- domain is narrow
- volume is low
- the agent is a prototype

### 3.2 RAG vs long context
Use RAG when:
- knowledge base is large
- documents change
- you need evidence

Use long context when:
- one artifact must be reasoned over end-to-end (one big log, one design fragment)

### 3.3 Autonomy tier
- Tier A: suggest only
- Tier B: read-only autonomous
- Tier C: writes with confirmation
- Tier D: full autonomy (rare)

### 3.4 Tools vs internal code
- use tools for system-of-record state
- use internal code for deterministic formatting/aggregation

### 3.5 Memory type
- session memory always
- long-term memory only for durable preferences/flags

### 3.6 Safety level
- read-only defaults
- write approvals for high-impact actions
- budget limits to stop runaway loops

---

## 4. Convert decisions into an implementation blueprint

### 4.1 Tool inventory
Create a tool catalog:
- tool name
- description
- input schema
- output schema
- side effects (R/W)
- scope constraints
- rate limits

### 4.2 Orchestrator state machine
Define states:
- route → plan → execute_tools → verify → refine → finalize

Define stop reasons:
- success
- needs_user
- tool_unavailable
- policy_blocked
- budget_exhausted

### 4.3 Evidence policy
For claims that must be grounded (specs/policy):
- require evidence ids
- block “spec claims” without citations

### 4.4 Write-action policy
For any state changes:
- prepare a change artifact (ticket payload, diff, plan)
- request approval
- execute with idempotency key
- verify post-condition

---

## 5. Reference runtime architecture

```text
Client
  → API Gateway (auth + quotas)
    → Orchestrator (loop control)
      → Model Router (model/mode)
      → Tool Gateway (allow-list + schemas)
      → RAG Service (retrieve + rerank)
      → Verifier (rules + invariants)
      → State Store (session + artifacts)
      → Observability (logs/metrics/traces)
      → Queue/Workflow Engine (async)
```

---

## 6. How this mapping appears in the two case studies

### 6.1 Customer Support Agent (example mapping)
- tools: orders/refunds/ticketing
- RAG: policies by region/category
- autonomy: Tier B/C
- verification: scope checks + schema + evidence
- success metric: resolution rate, CSAT proxy, cost per resolved ticket

### 6.2 Engineering/PCB Assistant (example mapping)
- tools: netlist/BOM/DRC + render
- RAG: datasheets/app notes + internal guidelines
- autonomy: Tier B/C (patch-based edits)
- verification: evidence-required specs + artifact references
- success metric: DRC reduction, evidence coverage, time-to-review

---

## 7. Operationalization checklist

### Build
- [ ] tool gateway with schemas + permissions
- [ ] orchestrator state machine + budgets
- [ ] retrieval pipeline with filters + rerank
- [ ] deterministic verifier gates

### Test
- [ ] golden workflows (end-to-end)
- [ ] tool mocks + replay harness
- [ ] retrieval regression set
- [ ] safety tests (policy bypass attempts)

### Deploy
- [ ] staged rollout (shadow/canary)
- [ ] cost monitoring
- [ ] incident playbook

---

## 8. Summary

The key to production agents is making **design decisions explicit**, then encoding them into:
- tools and schemas,
- orchestrator control logic,
- verification gates,
- and observable workflows.

This turns “agent demos” into **systems you can operate**.

[Previous](09_05_case_study_engineering_pcb_assistant.md) | [Next](10_conclusion_future_directions.md)
