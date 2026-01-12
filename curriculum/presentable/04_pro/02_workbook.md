# Level 4 Workbook: Pro (Frameworks, Reasoning Architectures, and Research Frontiers)

This workbook is the learner handout for the Pro level. It aligns to the slide deck `01_slides.md` and the four Pro chapters.

## Audience profile (who this is for)

Target learners:
- Expert developers and staff+ engineers building agent systems
- Architects designing production workflows with tools, memory, and governance
- Researchers/innovators translating papers into usable systems

Assumed background:
- Comfortable with Python and reading code
- Familiar with agent fundamentals (tools, memory, RAG, safety, observability)
- Able to reason about system design trade-offs (latency, cost, reliability, security)

## Goal

Build the ability to design and ship cutting-edge agent workflows with:
- explicit control flow (graphs/state machines)
- measurable reasoning architectures (search + constraints)
- robust tool boundaries (contracts, validation, policy)
- evaluation-driven iteration (benchmarks, CI gates, canaries)

## Learning outcomes

By the end of Level 4, you can:
- Choose an orchestration framework based on operational outcomes (testability, observability, safety).
- Implement a reasoning harness (candidates + scoring + selection) with budgets and verification.
- Design multi-agent workflows with role boundaries and artifact contracts.
- Run research-to-production experiments with metrics, ablations, and rollback plans.
- Build an internal evaluation suite that prevents regressions.

## Core materials (read in this order)

1. Slides: `01_slides.md`
2. Chapter 01: `chapter_01_advanced_frameworks.md`
3. Chapter 02: `chapter_02_reasoning_architectures.md`
4. Chapter 03: `chapter_03_agentic_design_patterns.md`
5. Chapter 04: `chapter_04_research_frontiers.md`

Supporting reference pack:
- Papers index: `papers/README.md`
- Research synthesis: `research_paper_analysis.md`
- Future trends: `future_trends_analysis.md`
- Patterns: `advanced_patterns_library.md`
- Evaluation: `benchmark_evaluation_framework.md`
- Implementation: `advanced_implementation_guide.md`

## Module plan (4 modules, 1 per chapter)

Each module includes objectives, reading, deliverables, and evidence to collect.

### Module 1: Advanced frameworks and workflow runtimes

Reading:
- `chapter_01_advanced_frameworks.md`

Objectives:
- Translate a workflow into explicit states and transitions.
- Add interrupts (approvals) and resumability design.
- Define a trace schema for debugging and audit.

Hands-on:
- Draft a workflow graph for a high-risk use case (write requires approval).
- Identify state fields, invariants, and stop conditions.

Deliverables:
- Workflow diagram + state definition
- Trace schema (fields you will log)
- Safety tier decision (read-only vs write-with-approval)

Evidence:
- A small transition test plan (what transitions are allowed/blocked)
- Example trace for one run (even if mocked)

### Module 2: Reasoning architectures and verification

Reading:
- `chapter_02_reasoning_architectures.md`

Objectives:
- Implement a reasoning harness: generate -> score -> select -> verify.
- Add retrieval gating and citation discipline for knowledge tasks.
- Define budgets and escalation rules for uncertainty.

Hands-on:
- Choose 1 workflow and define:
  - candidates to generate
  - deterministic constraints
  - scoring function
  - budgets and thresholds

Deliverables:
- Candidate schema + scoring rubric
- Retrieval gating rules (none/light/deep)
- Verification plan (deterministic first)

Evidence:
- A benchmark plan for 20 cases (golden set)
- Stability test plan (rerun the same case N times)

### Module 3: Agentic design patterns (tools + collaboration)

Reading:
- `chapter_03_agentic_design_patterns.md`

Objectives:
- Harden tool boundaries with contracts, validation, and authorization.
- Decide when multi-agent collaboration is justified.
- Add a verifier stage that can block invalid outputs.

Hands-on:
- Build a tool pipeline design:
  - discover -> validate -> authorize -> execute -> validate -> record
- If multi-agent:
  - define roles and artifact contracts

Deliverables:
- Tool contract checklist for your tool set
- Error handling plan (retry, fallback, degrade, escalate)
- Multi-agent role definitions (if used)

Evidence:
- Metrics you will track (invalid tool calls, recovery rate, cost per success)

### Module 4: Research frontiers and adoption discipline

Reading:
- `chapter_04_research_frontiers.md`

Objectives:
- Translate a paper mechanism into a bounded experiment.
- Build an adoption pipeline that is evaluation-driven.
- Identify platform investments with durable leverage.

Hands-on:
- Pick one paper from `papers/` and write an adopt-vs-monitor memo.
- Define success metrics, ablations, and rollback plan.

Deliverables:
- Experiment plan (1-2 pages)
- Benchmark impact estimate (expected delta and cost)
- "Adopt selectively" routing plan (where it applies and where it does not)

Evidence:
- A reproducible artifact list (traces, benchmark results, version ids)

## Capstone projects (pick 1-2)

1. Workflow-as-code (graph runtime)
   - Build a state-machine workflow with interrupts and approvals.
2. Reasoning harness (ToT-inspired)
   - Implement candidate generation + scoring only for high-risk decisions.
3. Evaluation platform slice
   - Build a benchmark runner + CI gate + scorecard report.
4. Safety runtime slice
   - Build policy gates + allowlists + audit logs for tool execution.

## Assessment rubric (how you know you are "pro")

A pro-grade submission includes:
- Traceability: clear traces and version ids for model/prompt/policy/tool
- Safety: explicit approvals and enforcement for high-risk actions
- Evaluation: benchmark evidence (offline + regression set)
- Reliability: retries/fallbacks/budgets designed and tested
- Cost awareness: cost per success tracked and bounded

## Notes on models and frameworks (pragmatic, vendor-agnostic)

This curriculum references:
- LangGraph as a graph/state-machine example
- modern model APIs (structured output, tool calling)

Your implementation should remain configurable:
- local models (Ollama) for learning and iteration
- hosted models for stronger capability when required

The pro move is not which model you pick. The pro move is how you measure and control the system.

