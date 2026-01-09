# Level 1 Workbook — Foundations & Mental Models (B1–B6)

**Goal:** Build correct mental models for what agents are, what they’re for, and the baseline architecture patterns.  
**Estimated time:** 2–3 weeks (or 3–5 sessions instructor-led).  
**Prereqs:** Basic programming + APIs + LLM basics.

## Level Outcomes

By the end of Level 1, learners can:

- Define an AI agent precisely (control loop + tools + state + verification)
- Identify workflows that benefit from agents vs deterministic automation
- Draw the 6-pillar architecture and explain information flow
- Describe current trends/patterns and choose a starting framework direction

## Deliverables (Evidence)

- A “workflow candidate backlog” (10+ workflows) with agent fit analysis
- A control-loop diagram for one selected workflow
- A 6-pillar architecture sketch for that workflow (boxes + arrows + responsibilities)
- A short framework selection rationale (2–5 paragraphs)

---

## B1 — Why AI Agents Now?

**Primary source:** `../../../../Agents/01_introduction_motivation.md`  
**Timebox:** 60–90 minutes

### Objectives

- Explain the limitations of traditional chatbots and script automation
- Describe enabling factors (models, tools, memory, organizational need)
- Articulate value to engineering, business, and end users

### Lecture Outline

1. The “inform → do” gap: why chatbots plateau
2. What changed recently (LLMs + tool APIs + retrieval + standard patterns)
3. Where agents create value: throughput, reliability, consistency, 24/7 operation
4. Organizational lens: agents as operational collaborators (not just assistants)

### Exercises

1. List 10 workflows in your org that require human orchestration today.
2. Classify each:
   - Information-only
   - Single action
   - Multi-step workflow (multiple systems)
3. Pick 2 workflows and write:
   - What makes this hard for deterministic automation?
   - What could an agent observe, plan, act on, and verify?

---

## B2 — What Is an AI Agent? (Core Definition)

**Primary source:** `../../../../Agents/02_what_is_an_ai_agent.md`  
**Timebox:** 60–90 minutes

### Objectives

- Define an AI agent using precise technical language
- Distinguish agents from chatbots, scripts, and “LLM wrappers”
- Describe Observe → Plan → Act → Verify → Refine

### Key Concepts (Short Form)

- Agent = LLM reasoning inside a control loop
- Tools are how agents affect external state (APIs, workflows, UI automation)
- Verification is mandatory in production (don’t trust a single model output)
- Autonomy is a design choice; gates are part of the product

### Exercises

1. Draw the control loop for: “Book a flight under $500 with 1 checked bag.”
2. Identify:
   - Observations (inputs, retrieved docs, tool results)
   - Plans (explicit steps + assumptions)
   - Actions (tool calls)
   - Verifications (what must be confirmed)
3. Rewrite this statement into a precise definition: “An agent is a better prompt.”

---

## B3 — What Problems Do Agents Solve?

**Primary source:** `../../../../Agents/03_what_problems_do_agents_solve.md`  
**Timebox:** 60–90 minutes

### Objectives

- Recognize common agent problem categories
- Identify limitations and anti-patterns
- Decide when NOT to use agents

### Decision Prompt (Use This Often)

> If the workflow is fixed, deterministic, and cheap, prefer deterministic automation.  
> If the workflow is variable, multi-step, tool-heavy, and needs judgment + verification, consider an agent.

### Exercises

For one workflow from B1:

- List required systems/tools (auth boundaries matter)
- Identify failure modes (tool failures, missing data, user ambiguity)
- Decide: agent vs workflow engine vs simple API
- Write a 5–10 sentence justification

---

## B4 — High-Level Architecture (The 6 Pillars)

**Primary source:** `../../../../Agents/04_high_level_architecture.md`  
**Timebox:** 90–120 minutes

### Objectives

- Draw the 6-pillar architecture from memory
- Explain each pillar and how they interact
- Understand why “LLM-only” designs fail in production

### The 6 Pillars (Mental Model)

1. User interface (chat, voice, ticketing system, IDE, etc.)
2. Agent orchestrator/controller (loop + policy enforcement)
3. LLM reasoning layer (one or more models)
4. Tools & integrations (APIs/workflows/UI automation)
5. Memory & knowledge (RAG, short-term, long-term)
6. Safety & observability (guardrails + logging/metrics/tracing)

### Exercises

1. Take your chosen workflow and sketch the 6 pillars (boxes + arrows).
2. For each pillar, answer:
   - What is the input?
   - What is the output?
   - What can go wrong?
3. Add at least 3 policy gates (e.g., “confirm before write”, “RBAC check”, “rate limit”).

---

## B5 — Evolution of Agent Systems (History & Context)

**Primary source:** `../../../../Agents/09_00_current_trends_and_patterns.md`  
**Timebox:** 60–90 minutes

### Objectives

- Explain how agent architectures evolved (capability + cost + safety)
- Recognize major trends (multi-model routing, retrieval, tool standardization)
- Understand why “single huge model” is rarely the production answer

### Exercises

- Pick a trend from the source doc and write:
  - What business constraint drove it (cost, latency, safety, complexity)?
  - What new failure mode did it introduce?
  - What countermeasure is needed (policy, eval, observability)?

---

## B6 — Frameworks Landscape Overview

**Primary sources:**

- `../../../../Agents/05_01_1_langchain.md`
- `../../../../Agents/05_01_3_langraph.md`
- `../../../../Agents/09_01_agent_frameworks_and_multi_agent_systems.md`

**Timebox:** 60–90 minutes

### Objectives

- Compare “loop-based controller” vs “graph/state-machine” orchestrations
- Understand where frameworks help (tooling/graph/runtime) vs don’t (product constraints)
- Make an explicit framework choice for your first build

### Selection Heuristics (Practical)

- If you need strict step control, retries, branching, and auditability → prefer graph/state-machine.
- If you need a lightweight prototype and you control the workflow tightly → a simple controller loop is enough.
- If your biggest risk is unsafe actions → start with read-only tools + strong confirmation gates (regardless of framework).

### Exercises

Create a 1-page selection note for your workflow:

- Constraints: latency, cost, data sources, risk level, tool complexity
- Orchestration style: loop vs graph
- Tool boundary: what is allowed, what is blocked
- MVP scope: what you will not automate yet

---

## Level 1 Hands-On Projects

Do these in order:

1. `projects/P01_faq_bot_with_rag.md`
2. `projects/P02_intent_router.md`

---

## Knowledge Check (5–10 minutes)

- Explain, in 3 sentences, why “agents are distributed systems.”
- Give two examples of workflows that should NOT be implemented as agents and why.
- What are the minimum components you need for a safe “read-only” agent MVP?
