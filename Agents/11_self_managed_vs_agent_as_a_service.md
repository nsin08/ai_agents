[Previous](10_conclusion_future_directions.md) | [Next](12_01_customer_support_agent_architecture.md)

# Self-Managed Agent Infrastructure vs Agent-as-a-Service  

## Table of Contents

- [1. Definitions (keep the layers straight)](#1-definitions-keep-the-layers-straight)
  - [1.1 Selfƒ?`managed agent infrastructure](#11-selfmanaged-agent-infrastructure)
  - [1.2 Agentƒ?`asƒ?`aƒ?`Service (managed)](#12-agentasaservice-managed)
- [2. The honest tradeoff: what you get vs what you lose](#2-the-honest-tradeoff-what-you-get-vs-what-you-lose)
  - [2.1 Why managed services usually win (for most teams)](#21-why-managed-services-usually-win-for-most-teams)
  - [2.2 Why selfƒ?`managed can be worth it](#22-why-selfmanaged-can-be-worth-it)
- [3. Decision rule (simple, brutal)](#3-decision-rule-simple-brutal)
- [4. Practical comparison matrix](#4-practical-comparison-matrix)
- [5. Edge cases where you *must* build or heavily selfƒ?`manage](#5-edge-cases-where-you-must-build-or-heavily-selfmanage)
  - [5.1 Hard data residency / sovereignty](#51-hard-data-residency-sovereignty)
  - [5.2 Airƒ?`gapped or restricted networks](#52-airgapped-or-restricted-networks)
  - [5.3 Highƒ?`risk write actions](#53-highrisk-write-actions)
  - [5.4 Extreme observability and audit requirements](#54-extreme-observability-and-audit-requirements)
  - [5.5 Massive tool surface or dynamic tool discovery](#55-massive-tool-surface-or-dynamic-tool-discovery)
  - [5.6 Unit economics at scale](#56-unit-economics-at-scale)
  - [5.7 Specialized modalities (medical imaging, engineering files)](#57-specialized-modalities-medical-imaging-engineering-files)
- [6. Recommended architecture pattern: Hybrid (usually best)](#6-recommended-architecture-pattern-hybrid-usually-best)
  - [6.1 What stays in your environment](#61-what-stays-in-your-environment)
  - [6.2 What you delegate to the vendor](#62-what-you-delegate-to-the-vendor)
- [7. Migration strategy (realistic path)](#7-migration-strategy-realistic-path)
- [8. Common failure modes (what breaks in real life)](#8-common-failure-modes-what-breaks-in-real-life)
  - [In Agentƒ?`asƒ?`aƒ?`Service](#in-agentasaservice)
  - [In selfƒ?`managed](#in-selfmanaged)
- [9. Final guidance](#9-final-guidance)

# 11 ƒ?" Selfƒ?`Managed Agent Infrastructure vs Agentƒ?`asƒ?`aƒ?`Service

> **Goal:** Provide a pragmatic comparison of (A) building/operating your own agent platform vs (B) using a managed agent service (cloud or vendor), and list the edge cases where selfƒ?`managed is required or clearly advantageous.

---

## 1. Definitions (keep the layers straight)

### 1.1 Selfƒ?`managed agent infrastructure
You own and operate most of the stack:
- model hosting / routing
- tool gateway (APIs, DBs, logs, file parsers)
- retrieval system (search, embeddings, vector index)
- memory stores
- orchestration runtime (state machine / workflow engine)
- policy enforcement (RBAC, allowlists, approvals)
- observability, evaluation, rollout

### 1.2 Agentƒ?`asƒ?`aƒ?`Service (managed)
A vendor provides the ƒ?oagent runtimeƒ?? and often parts of:
- model hosting
- tool calling interface
- session/state handling
- guardrails integrations
- managed retrieval stores
- monitoring dashboards

You still provide:
- your business tools/APIs (connectors)
- your data governance
- your evaluation and QA
- your domain workflows

---

## 2. The honest tradeoff: what you get vs what you lose

### 2.1 Why managed services usually win (for most teams)
**Benefits**
- fastest timeƒ?`toƒ?`value (weeks vs months)
- fewer distributedƒ?`systems failures to debug
- managed scaling, retries, rate limiting primitives
- security posture is ƒ?ogood enoughƒ?? for many orgs
- strong integration ecosystem (connectors, SDKs)

**Costs / limitations**
- less control over orchestration internals
- vendor lockƒ?`in (tool format, policies, tracing)
- less tunability for retrieval quality and caching strategy
- constraints around data residency and logging
- harder to do deep customization (custom planners, critics, special schedulers)

### 2.2 Why selfƒ?`managed can be worth it
**Benefits**
- full control over autonomy tiers, verification gates, and orchestration graphs
- tight integration with existing internal platforms (identity, audit, logging)
- optimized cost at high scale (caching, routing, batching, model choice)
- portability across clouds/vendors
- easier to enforce strict governance when you control every hop

**Costs**
- you are now running a complex platform (on-call burden)
- retrieval quality becomes your problem (chunking, rerankers, evals)
- security and compliance require real engineering (not prompts)
- longer iteration cycle; higher maintenance

---

## 3. Decision rule (simple, brutal)

Use **Agentƒ?`asƒ?`aƒ?`Service by default**.

Choose **selfƒ?`managed** only when one or more of the following is true:
- you **cannot** send data to a vendor runtime
- you need **nonƒ?`negotiable** control over orchestration + safety gates
- you must operate in **airƒ?`gapped/onƒ?`prem** environments
- your cost at scale makes managed pricing unsustainable
- your tool surface is massive and you need custom discovery/routing at runtime
- your domain is highƒ?`risk and requires deterministic, auditable verification at every step

---

## 4. Practical comparison matrix

| Dimension | Agentƒ?`asƒ?`aƒ?`Service | Selfƒ?`Managed |
|---|---|---|
| Timeƒ?`toƒ?`production | Fast | Slow/medium |
| Infra complexity | Low | High |
| Orchestration flexibility | Medium | Highest |
| Data residency constraints | Sometimes limited | Fully controllable |
| Deep tool governance | Medium (vendor dependent) | Full control |
| Evaluation ownership | You still own it | You still own it |
| Observability depth | Good, but vendor shaped | Full control |
| Lockƒ?`in risk | Medium/high | Lower (if well designed) |
| Cost at high scale | Can grow fast | Potentially optimized |

---

## 5. Edge cases where you *must* build or heavily selfƒ?`manage

### 5.1 Hard data residency / sovereignty
- sensitive data cannot leave network boundary
- strict regional storage and processing rules

**Implication:** selfƒ?`host model + retrieval + tool gateway, or a hybrid with strict isolation.

### 5.2 Airƒ?`gapped or restricted networks
- manufacturing, defense, regulated plants, offline facilities

**Implication:** selfƒ?`managed runtime; tool calls must remain local.

### 5.3 Highƒ?`risk write actions
- agents that can change production systems, approve payouts, modify identity/access

**Implication:** you need strong deterministic gates:
- patch/diff workflows
- approval steps
- idempotency keys
- postƒ?`condition verification

Managed services may be usable, but only if they support your exact control model.

### 5.4 Extreme observability and audit requirements
- endƒ?`toƒ?`end traces with tool inputs/outputs, redaction rules, retention policies

**Implication:** selfƒ?`managed or hybrid where vendor sees only nonƒ?`sensitive context.

### 5.5 Massive tool surface or dynamic tool discovery
- hundreds to thousands of internal APIs
- evolving tools across teams

**Implication:** you likely need a tool registry + policy engine you control.

### 5.6 Unit economics at scale
- very high query volume, long contexts, frequent retrieval

**Implication:** custom caching, batching, embedding strategy, model routing to control cost.

### 5.7 Specialized modalities (medical imaging, engineering files)
- needs custom parsers, domain validators, and evidence workflows

**Implication:** selfƒ?`managed tool layer is mandatory; managed runtime may still be used for reasoning.

---

## 6. Recommended architecture pattern: Hybrid (usually best)

Use managed agent runtime **for reasoning + tool calling**, but keep sensitive and complex parts in your environment.

### 6.1 What stays in your environment
- tool gateway (logs, SQL, ticketing, object store fetch)
- retrieval service (optional; or vendorƒ?`managed retrieval if allowed)
- policy enforcement (RBAC, tenant isolation)
- evaluation harness + golden tests

### 6.2 What you delegate to the vendor
- model hosting and scaling
- baseline orchestration
- streaming responses
- simple session handling

**Key idea:** vendor is your ƒ?obrain provider,ƒ?? your environment remains the ƒ?osystem of record.ƒ??

---

## 7. Migration strategy (realistic path)

1) Start with managed agent runtime + **readƒ?`only tools**
2) Add retrieval for doc corpora (manuals/runbooks) with strict evidence policy
3) Introduce deterministic verifiers (schemas, business rules)
4) Add controlled write actions (approval gates)
5) If/when constraints hit (residency, cost, control), move individual components selfƒ?`managed:
   - retrieval first (common)
   - tool gateway / policy engine
   - finally model hosting if necessary

---

## 8. Common failure modes (what breaks in real life)

### In Agentƒ?`asƒ?`aƒ?`Service
- tool sprawl without governance
- poor retrieval quality (garbage in, confident out)
- insufficient audit logging for regulated workflows
- unexpected cost growth from long contexts + tool loops

### In selfƒ?`managed
- underestimating ops burden (on-call, scaling, incident response)
- no evaluation harness ƒ+' regressions ship silently
- weak permissions and scoping ƒ+' data leakage risk
- overƒ?`engineering before proving product value

---

## 9. Final guidance

- If youƒ?Tre proving value: **managed wins**.
- If youƒ?Tre meeting strict governance/residency or operating at extreme scale: **selfƒ?`managed or hybrid**.
- Regardless of choice, the real moat is:
  - tool correctness + schemas
  - deterministic verification
  - evaluation harness
  - observability

Those decide whether an agent is a demo or a production system.

[Previous](10_conclusion_future_directions.md) | [Next](12_01_customer_support_agent_architecture.md)
