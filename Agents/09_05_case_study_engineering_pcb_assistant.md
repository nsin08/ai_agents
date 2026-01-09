[Previous](09_04_case_study_customer_support_agent.md) | [Next](09_06_architecture_decisions_mapping_to_system.md)

# Case Study: Engineering PCB Assistant  

## Table of Contents

- [**Case Study — Engineering / PCB Assistant (End-to-End Architecture Mapping)**](#case-study-engineering-pcb-assistant-end-to-end-architecture-mapping)
- [1. Use case overview](#1-use-case-overview)
  - [What the agent should handle](#what-the-agent-should-handle)
  - [What the agent must NOT do](#what-the-agent-must-not-do)
- [2. System actors and data sources](#2-system-actors-and-data-sources)
  - [Actors](#actors)
  - [Inputs](#inputs)
- [3. Architecture (mapped to core components)](#3-architecture-mapped-to-core-components)
  - [3.1 High-level runtime flow](#31-high-level-runtime-flow)
  - [3.2 Multi-LLM roles (recommended)](#32-multi-llm-roles-recommended)
- [4. Tools layer (the “hands”)](#4-tools-layer-the-hands)
  - [4.1 Typical tools](#41-typical-tools)
  - [4.2 Tool gateway responsibilities](#42-tool-gateway-responsibilities)
- [5. Retrieval (RAG) + evidence strategy](#5-retrieval-rag-evidence-strategy)
  - [5.1 What RAG is used for](#51-what-rag-is-used-for)
  - [5.2 Retrieval best practices](#52-retrieval-best-practices)
- [6. Memory strategy](#6-memory-strategy)
  - [6.1 Session (ephemeral)](#61-session-ephemeral)
  - [6.2 Long-term memory (selective)](#62-long-term-memory-selective)
- [7. Guardrails and safety tier](#7-guardrails-and-safety-tier)
- [8. Mapping decisions to the decision tree](#8-mapping-decisions-to-the-decision-tree)
  - [Single vs multi-LLM](#single-vs-multi-llm)
  - [RAG vs long context](#rag-vs-long-context)
  - [Autonomy](#autonomy)
  - [Tools vs internal code](#tools-vs-internal-code)
  - [Memory](#memory)
- [9. Example end-to-end workflow](#9-example-end-to-end-workflow)
  - [User request](#user-request)
  - [9.1 Planner output (illustrative)](#91-planner-output-illustrative)
  - [9.2 Verification gates](#92-verification-gates)
  - [9.3 Output](#93-output)
- [10. Observability and evaluation](#10-observability-and-evaluation)
  - [What to trace](#what-to-trace)
  - [Metrics](#metrics)
- [11. Summary](#11-summary)


## **Case Study — Engineering / PCB Assistant (End-to-End Architecture Mapping)**

This case study maps the agent architecture and design decisions to a real technical assistant: an **Engineering/PCB Agent** that helps with schematic/PCB review, component selection, BOM work, and design-rule validation — while keeping **safety, IP protection, and determinism** as first-class requirements.

---

## 1. Use case overview

### What the agent should handle
- **Schematic understanding**: “Explain this circuit block”
- **PCB review**: “Any obvious layout issues? clearance? return paths?”
- **BOM analysis**: “Generate / normalize BOM, suggest alternates”
- **Datasheet grounding**: “Compare these regulators; pick one for 24V→5V @ 2A”
- **Rule checks**: “Run DRC/ERC and summarize failures”
- **Manufacturing readiness**: “Gerber checklist, assembly constraints, fiducials”
- **Troubleshooting**: “Why is the ADC noisy? what measurements to take?”

### What the agent must NOT do
- fabricate facts about specs; it must cite datasheets / evidence
- change design files silently
- access other projects or tenants
- produce instructions for weaponization or harmful devices

---

## 2. System actors and data sources

### Actors
- **Engineer** (user)
- **Design repository** (Git/PLM)
- **EDA toolchain** (KiCad/Altium/OrCAD exports)
- **Part catalog** (internal database / supplier feeds)
- **Docs store** (datasheets, app notes, errata)
- **CI pipelines** (DRC/ERC automation, BOM linting)

### Inputs
- EDA project files (or exports): netlist, schematic PDFs, PCB files, pick-and-place
- Datasheets (PDFs)
- Requirements: voltage/current, thermal limits, cost, availability
- Constraints: stackup, rules, manufacturing capabilities

---

## 3. Architecture (mapped to core components)

### 3.1 High-level runtime flow

```text
Engineer UI (web/IDE plugin)
  → API Gateway (auth + project scoping)
    → Orchestrator (Plan → Verify → Refine)
      → Model Router (choose mode + models)
      → RAG Service (datasheets/app notes/runbooks)
      → Tool Gateway (EDA parsers, DRC runners, BOM tools)
      → Verifier (schemas + invariants + evidence)
      → State Store (session + run artifacts)
      → Observability (logs/metrics/traces)
```

### 3.2 Multi-LLM roles (recommended)
- **Router**: route between quick Q&A vs deep analysis
- **Planner**: produce structured plan (e.g., which checks to run)
- **Executor**: form tool arguments, interpret outputs
- **Verifier**: deterministic checks + evidence requirements
- **Finalizer**: engineer-friendly report formatting

---

## 4. Tools layer (the “hands”)

A PCB assistant is tool-heavy. Most reliability comes from making tools authoritative.

### 4.1 Typical tools

**Read/inspect tools (safe default)**
- `parse_netlist(project_id)` → nets, components, pins
- `extract_bom(project_id)` → BOM rows
- `run_erc(project_id)` / `run_drc(project_id)` → violations
- `render_schematic_block(block_id)` → image/pdf snippet reference
- `search_parts(query, constraints)` → candidate parts + metadata

**Compute/simulation tools (bounded)**
- `spice_simulate(netlist_fragment, stimulus)` → waveforms/metrics
- `thermal_estimate(component, load, ambient)` → estimate

**Write tools (gated)**
- `propose_bom_substitution(refdes, new_part)` → patch/diff artifact
- `apply_patch(project_id, patch_id)` → requires approval

### 4.2 Tool gateway responsibilities
- strict schema validation
- project/tenant scoping
- allow-list per workflow and per role
- redaction of proprietary identifiers where needed
- idempotency keys for any write action

---

## 5. Retrieval (RAG) + evidence strategy

### 5.1 What RAG is used for
- datasheets (electrical limits, abs max, pin functions)
- app notes (layout recommendations, compensation networks)
- errata and known issues
- internal design guidelines (stackup, clearance, ESD rules)

### 5.2 Retrieval best practices
- chunk by semantic sections (Electrical Characteristics, Typical Application)
- store metadata: part number, revision, vendor, voltage range
- rerank results; cap top-k
- always attach evidence references to conclusions

**Rule:** if a claim is spec-related, it must be grounded to datasheet evidence.

---

## 6. Memory strategy

### 6.1 Session (ephemeral)
- active project context
- requirements for this design (voltage/current/constraints)
- tool outputs (DRC, BOM results)

### 6.2 Long-term memory (selective)
Store only high-value, low-risk preferences:
- preferred vendors
- standard footprints used in org
- manufacturing constraints by site

Avoid storing:
- full design content
- proprietary net names
- raw file contents (unless explicitly governed)

---

## 7. Guardrails and safety tier

Recommended safety tier:
- **Tier 1** for inspection + analysis (read-only)
- **Tier 2** for proposed edits (patch-only + approval)

Key guardrails:
- read-only by default
- any file change must be produced as a **diff/patch artifact**
- explicit approval required before applying changes
- limit simulations (prevent runaway cost)
- prevent cross-project leakage

---

## 8. Mapping decisions to the decision tree

### Single vs multi-LLM
- Prefer **multi-LLM**: mixed difficulty tasks + structured tool use + reports.

### RAG vs long context
- Use **RAG** for datasheets/app notes/guidelines.
- Use **long context** only for a contained artifact (e.g., one netlist fragment) when end-to-end reasoning is required.

### Autonomy
- Mostly **Tier B (read-only autonomous)**
- **Tier C (write with confirmation)** only for patch application.

### Tools vs internal code
- Specs, inventory, DRC results: tools (authoritative)
- Formatting, unit conversions, simple computations: internal code

### Memory
- Session state + artifact references
- minimal long-term preferences

---

## 9. Example end-to-end workflow

### User request
“Check my buck converter layout and tell me why it’s noisy.”

### 9.1 Planner output (illustrative)

```json
{
  "goal": "Diagnose switching noise in buck converter section",
  "constraints": {"mode": "read_only", "max_steps": 10, "max_tool_calls": 6},
  "steps": [
    {"id": 1, "action": "tool", "name": "render_pcb_region", "args": {"region": "buck_converter"}},
    {"id": 2, "action": "tool", "name": "extract_buck_nets", "args": {"region": "buck_converter"}},
    {"id": 3, "action": "retrieve", "name": "rag_search", "args": {"query": "buck converter layout loop area hot loop recommendations", "filters": {"vendor": "${controller_vendor}"}}},
    {"id": 4, "action": "tool", "name": "run_drc", "args": {"project_id": "${project_id}", "ruleset": "hf_switching"}},
    {"id": 5, "action": "verify", "checks": ["schema", "evidence", "consistency"]},
    {"id": 6, "action": "respond"}
  ]
}
```

### 9.2 Verification gates
- claims about recommended placement/loop area must be backed by retrieved app note evidence
- DRC results must be parsed and referenced
- if evidence is insufficient → ask for missing context (stackup, switching frequency, load)

### 9.3 Output
- a structured report:
  - suspected noise sources
  - evidence references (app note sections)
  - PCB observations (hot loop, return path, via placement)
  - recommended rework steps
  - optional patch suggestion (as diff), *not applied*

---

## 10. Observability and evaluation

### What to trace
- which artifacts were loaded (project_id, revision)
- which tools ran (DRC/ERC, render)
- which evidence chunks were used
- stop reasons and budget usage

### Metrics
- “evidence coverage rate” for spec claims
- DRC/analysis success rate
- escalation rate (“needs user data”)
- cost per completed review

---

## 11. Summary

A PCB assistant becomes production-ready when:
- tools are authoritative,
- retrieval grounds all spec claims,
- edits are patch-based and approved,
- and the orchestrator enforces bounded Plan → Verify → Refine.

Next: a generic mapping document — **09_06_architecture_decisions_mapping_to_system.md**

[Previous](09_04_case_study_customer_support_agent.md) | [Next](09_06_architecture_decisions_mapping_to_system.md)
