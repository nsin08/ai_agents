# Level 2 Workbook — Intermediate Curriculum

**Goal:** Move from “working demos” to “repeatable system design” using the reusable core (`src/agent_labs/`) and labs (`labs/03`–`labs/06`).  
**Timebox:** ~15–20 hours (self-study) or 6–10 instructor-led sessions.  
**Prereqs:** Level 1 outcomes + Python async/await comfort.

## Level 2 Deliverables (evidence)

By the end of this workbook, you should have:

- An orchestrator/controller spec (states, transitions, stop conditions, retry rules)
- A memory design (short/long/RAG) with explicit write + retrieval policies
- A context packing plan (token budget + overflow strategy)
- An observability plan (logs + traces + metrics + “how we debug” checklist)
- A resilient tool integration plan (contracts + validation + error handling)

## Setup

From repo root:

```powershell
uv venv
uv pip install -e ".[dev]"
```

Optional if you don’t install editable:

```powershell
$env:PYTHONPATH = "src"
```

## How to use this workbook

Each chapter below includes:

- Objectives (what you should learn)
- Pointers (what files to read in `src/agent_labs/`)
- One hands-on exercise (minimum) with suggested acceptance criteria

Use the chapter texts for theory:

- `curriculum/presentable/02_intermediate/chapter_01_orchestrator_patterns.md`
- …
- `curriculum/presentable/02_intermediate/chapter_06_integration_patterns.md`

## I1 — Orchestrator Patterns (Lab 03)

**Read:** `curriculum/presentable/02_intermediate/chapter_01_orchestrator_patterns.md`  
**Lab:** `labs/03/README.md`  
**Core modules:** `src/agent_labs/orchestrator/`

### Objectives

- Define a control loop (OPRV) with explicit stop conditions
- Separate planning vs execution vs verification failures
- Model execution as a state machine

### Exercise (deliverable: controller spec)

Write a 1-page “controller spec” for an agent in your domain:

- States + valid transitions
- Stop conditions (max turns, cost, latency)
- Retry policy and when to stop retrying

**Acceptance criteria:**

- Spec includes at least 6 states and explicit failure transitions
- Includes at least 3 failure modes + corresponding handling
- Includes at least 2 metrics you will emit for debugging

## I2 — Advanced Memory (Lab 04)

**Read:** `curriculum/presentable/02_intermediate/chapter_02_advanced_memory.md`  
**Lab:** `labs/04/README.md`  
**Core modules:** `src/agent_labs/memory/`

### Objectives

- Explain why short/long/RAG are different tiers
- Define a write policy (what can be persisted)
- Define a retrieval policy (what can enter context)

### Exercise (deliverable: memory architecture + policy)

Create a memory architecture diagram (ASCII is fine) and policies:

- Short-term capacity strategy (window size, eviction)
- Long-term storage strategy (what keys / what format)
- RAG ingestion + retrieval strategy (chunk size, filters)

**Acceptance criteria:**

- Includes at least 3 “do not store” rules (privacy / contamination)
- Includes at least 3 “do not retrieve” rules (risk / irrelevance)
- Includes one strategy for “conflicting facts”

## I3 — Context Engineering (Lab 05)

**Read:** `curriculum/presentable/02_intermediate/chapter_03_context_engineering.md`  
**Lab:** `labs/05/README.md`  
**Core modules:** `src/agent_labs/context/`

### Objectives

- Use prompt templates and variables correctly
- Create a token budget and enforce it
- Choose an overflow strategy (truncate vs summarize vs retrieve)

### Exercise (deliverable: packing plan)

Create a context packing plan for a multi-step task:

- Required fields (must-have)
- Optional fields (nice-to-have)
- Overflow policy (what gets dropped first)
- Citation strategy (how you prevent “source-less claims”)

**Acceptance criteria:**

- Budget defined (max tokens) + prioritization order
- Strategy specified for overflow and “very long user messages”
- Plan includes a “safety / injection” section (what you strip/ignore)

## I4 — Observability (Lab 06)

**Read:** `curriculum/presentable/02_intermediate/chapter_04_observability.md`  
**Lab:** `labs/06/README.md`  
**Core modules:** `src/agent_labs/observability/`

### Objectives

- Emit structured logs with correlation IDs
- Trace the OPRV steps with span timing
- Track basic metrics (latency, errors, tool calls)

### Exercise (deliverable: observability checklist)

Write a debugging checklist for “agent produced wrong output”:

- What logs do we check first?
- What spans should exist and what is “too slow”?
- What metrics indicate degradation?
- What artifacts must be captured for reproductions?

**Acceptance criteria:**

- Checklist includes at least 5 log fields you require
- Includes at least 3 spans you expect to see
- Includes at least 3 metrics and their alert thresholds

## I5 — Multi-Turn Conversations

**Read:** `curriculum/presentable/02_intermediate/chapter_05_multi_turn_conversations.md`  
**Core modules:** `src/agent_labs/orchestrator/context.py`, `src/agent_labs/context/window.py`

### Objectives

- Model conversation state (known/unknown slots)
- Decide what stays in short-term vs summary vs long-term
- Apply repair strategies for incomplete user input

### Exercise (deliverable: state + repair plan)

Pick a real conversation (support triage, onboarding, PR review). Define:

- Required slots (must collect)
- Optional slots (good-to-have)
- Repair prompts when a slot is missing/invalid

**Acceptance criteria:**

- At least 5 required slots + validation rules
- At least 3 repair strategies (clarify, confirm, reframe)
- Explicit rule for when you stop asking and escalate

## I6 — Integration Patterns (Tools)

**Read:** `curriculum/presentable/02_intermediate/chapter_06_integration_patterns.md`  
**Core modules:** `src/agent_labs/tools/`

### Objectives

- Define tool contracts (schema, constraints, side effects)
- Implement tool discovery + validation + execution
- Handle tool errors deterministically

### Exercise (deliverable: tool contract + error handling)

Define 2 tools for your domain as contracts (Markdown or JSON):

- `name`, `description`
- `input_schema`, `output_schema`
- constraints (timeout, retries)
- side effects (read/write) + gating (confirm/human approval)

Then write an error-handling plan:

- invalid inputs
- missing tools
- tool failures

**Acceptance criteria:**

- Contracts include input + output schema
- Clear statement of side effects and gating rules
- Error plan includes at least 3 failure scenarios and expected agent behavior

---

## Verified runnable snippets (optional, recommended)

Run examples that are verified by tests:

- `curriculum/presentable/02_intermediate/snippets/README.md`

