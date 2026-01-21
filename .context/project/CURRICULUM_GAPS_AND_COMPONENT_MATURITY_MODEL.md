# Curriculum + Labs Gap Analysis + Component Maturity Model (with `agent_core`)

**Date:** 2026-01-20  
**Scope:** Full repository scan (`src/`, `labs/`, `curriculum/`, `Agents/`)

This document identifies gaps in the curriculum + labs and outlines a maturity model for core agent components. It proposes a learning progression: start from scratch in `agent_labs`, productionize into `agent_core`, and optionally demonstrate industry adoption via adapter layers for popular ecosystems (e.g., LangChain/LangGraph).

---

## 1) Executive Summary

The repository establishes a strong educational baseline (Levels 1-2) for building AI agents (orchestration, memory tiers, tools, safety, observability). To reach production-grade systems (Levels 3-4), the missing pieces are mostly about standardization, persistence, and engineering discipline.

**Key findings**
1. **Educational core is solid**: Labs 01-08 cover the fundamental lifecycle well.
2. **MCP is the major tool integration gap**: Model Context Protocol is absent from code and labs, but increasingly important for standardized tool servers and remote tool boundaries.
3. **Persistence needs a production path**: current defaults (`sqlite`, in-memory) are correct for learning but do not demonstrate scalable deployments (Postgres/Redis/pgvector or managed vector DB).
4. **Evaluation is not a gate**: evaluation modules exist, but there is no repeatable "ship gate" workflow (golden sets + CI regression + stability tests).
5. **Add a production-ready importable core**: introduce `src/agent_core/` as a configurable, scalable framework layer (factories/registries/policies, production backends, OTel export, evaluation gates, checkpoint/resume) that real projects can import directly.
6. **Add optional ecosystem interop**: show how the same `agent_core` concepts map into LangChain (integration ecosystem) and LangGraph (workflow runtime) without making the learning path depend on those frameworks.

---

## 2) Repository Layering (Why `agent_core` Changes the Plan)

To keep learning code readable while enabling production readiness:

- `src/agent_labs/`: educational/reference implementations (minimal dependencies, clarity-first).
- `src/agent_core/` (proposed): production framework components (configurable, scalable, operable).
- `src/agent_recipes/` (optional): composed workflows built from `agent_core` ("ready-made recipes").
- `src/agent_lc/` (optional): LangChain adapters that wrap `agent_core` primitives as LangChain components (Tools/Retrievers/Callbacks).
- `src/agent_lg/` (optional): LangGraph adapters that run `agent_core` steps as graph nodes with state + checkpoint/resume integration.
- `labs/`: hands-on exercises that can start with `agent_labs`, then upgrade to `agent_core`.

**Design pattern scope impact**
- Implement "platform patterns" (factories, registries, routing, policies) primarily in `agent_core`.
- Keep `agent_labs` mostly at Level 1-2 (interfaces + simple DI) unless a lab explicitly teaches refactoring patterns.
- Keep LangChain/LangGraph usage (if any) at the edges (`agent_lc`/`agent_lg`) so the core stays vendor- and framework-neutral.

---

## 3) Coverage Map & Maturity Assessment (Current vs Target)

Maturity levels used below:
- **Level 0**: hardcoded
- **Level 1**: interface + one impl
- **Level 2**: configurable (factory/config)
- **Level 3**: registry/platform (runtime selection, plugins)
- **Level 4**: adaptive (telemetry-driven routing + eval-gated rollouts)

| Component | Current state | Current level | Target level | Main gap to close |
|---|---|---:|---:|---|
| Orchestrator | Implemented (`src/agent_labs/orchestrator`) | 2 | 3 | checkpoint/resume, idempotency, durable run state |
| Tools | Registry + validation (`src/agent_labs/tools`) | 2 | 3 | MCP support + remote tool boundaries + authZ/audit |
| Memory | Tiers exist (Lab 04, `src/agent_labs/memory`) | 1-2 | 3 | production backends (Postgres/Redis/vector), policies, multi-tenant |
| Context | Chunking/templates/window (`src/agent_labs/context`) | 1-2 | 3 | context packing policy + retrieval gating + evidence discipline |
| Retrieval / RAG | Mostly educational; Chroma scaffold exists | 1-2 | 3 | hybrid retrieval, metadata filters, reranking, vector ops story |
| Observability | JSON logs/traces (`src/agent_labs/observability`) | 2 | 3 | OTel export + trace context propagation |
| Safety | Guardrails (Lab 07, `src/agent_labs/safety`) | 2 | 3 | context-aware policies, tenant/user tiers, audit integration |
| Evaluation | Basic scorers/runner (`src/agent_labs/evaluation`) | 1 | 3 | CI gates, golden sets, stability tests, scorecards |
| Multi-agent | Router/decomposition lab exists (Lab 08) | 2 | 3 | distributed execution boundaries + shared state governance |
| Production core package | Not present | 0 | 3 | create `agent_core` as the stable import surface |

---

## 4) Detailed Gap Analysis (What "Production Grade" Requires)

### 4.1 Model Context Protocol (MCP) (Critical)

**Status:** referenced in case-study material; absent from `src` and `labs`.  
**Why it matters:** standard tool discovery + invocation; clean boundary for permissions and audit; reduces N-tools x M-agents integration sprawl.  
**Missing pieces:** MCP client adapter, tool schema mapping, error taxonomy mapping, telemetry correlation, security posture for remote tools.

### 4.2 Production persistence strategy (High)

**Status:** only `SqliteStorage` and `InMemoryStorage` are implemented; vector backend is placeholder/scaffold.  
**Why it matters:** production agents need multi-tenant isolation, concurrent writes, and scalable retrieval.  
**Missing pieces:** Postgres/MySQL backend, Redis session store, migrations/versioning, backup/restore assumptions, clear "when SQLite is okay" guidance.

### 4.3 Vector DB + retrieval maturity (High)

**Status:** vector concepts are taught; Chroma appears as an exercise scaffold; no production retrieval policy layer.  
**Why it matters:** retrieval quality and cost dominate many agent workflows.  
**Missing pieces:** metadata filters, hybrid retrieval (keyword + vector), reranking, provenance/citations, fallback modes when vector store degrades.

### 4.4 Graph DB / knowledge graph retrieval (Optional, but valuable)

**Status:** absent.  
**When it matters:** relationship-heavy domains (org/service graphs, incident graphs, asset dependency trees, authorization graphs).  
**Missing pieces:** decision criteria (when graph is worth it), integration pattern (graph query + retrieval packer), evaluation cases.

### 4.5 Context packing + retrieval gating policy (High)

**Status:** templates/token budgeting/chunking exist; no unified packing policy.  
**Missing pieces:** deterministic packing order, retrieval gating (none/light/deep), evidence manifest (what was included and why), injection hygiene for retrieved content.

### 4.6 Memory tiers: policy + consolidation (High)

**Status:** tiers exist, but "store everything everywhere" is the default behavior.  
**Missing pieces:** write policy, consolidation pipeline (episodes -> facts -> dedupe/merge), retention/TTL/redaction, tenant-scoped keys, replay safety.

### 4.7 Evaluation as code + CI release gates (High)

**Status:** evaluators exist; no end-to-end workflow.  
**Missing pieces:** golden datasets, baseline vs candidate comparisons, CI gate, stability tests (rerun N times), scorecards, promotion criteria.

### 4.8 OpenTelemetry (OTel) integration (Medium)

**Status:** custom JSON logging + traces exist; OTel is referenced, not implemented.  
**Missing pieces:** trace context propagation, OTel exporter, mapping from internal trace schema to spans/metrics.

### 4.9 Checkpoint/resume for long-running workflows (Medium)

**Status:** mentioned conceptually; no runnable end-to-end path.  
**Missing pieces:** run state model, idempotency rules, resume UX, correlation IDs across resumes.

### 4.10 Model routing/cascade/fallback (Medium)

**Status:** multiple providers exist; routing is not first-class.  
**Missing pieces:** routing policy, capability registry, cost/latency-aware selection, health-based fallback (cloud -> local), eval-gated rollout.

### 4.11 Framework interop examples (LangChain / LangGraph) (Medium)

**Status:** not covered explicitly; the repo is intentionally framework-agnostic.  
**Why it matters:** teams often already run LangChain/LangGraph (or evaluate them) and will ask "how does this map?". A small, well-framed example reduces translation friction when integrating into existing codebases.  
**What it solves in practice:**
- **LangChain**: reduces "integration plumbing" by providing a large ecosystem of tool/retriever/document-loader integrations and common composition patterns.
- **LangGraph**: reduces "workflow plumbing" by providing an explicit state-machine/graph runtime for multi-step flows (branching, retries, checkpoints/resume, human-in-the-loop).
**Missing pieces (without creating a hard dependency):**
- Concept mapping: `ToolRegistry` <-> LangChain Tools, retrieval (`VectorIndex`/retrievers) <-> LangChain Retrievers, orchestrator loop <-> LangGraph nodes/edges/state.
- Boundary guidance: keep `agent_core` as the stable production surface; treat LangChain/LangGraph as optional adapters at the edge.
- Minimal adapter examples (optional): "wrap a LangChain tool as a repo `ToolContract`" and/or "run a repo agent step inside a LangGraph node".

---

## 5) Design Patterns: What to Implement Where (with `agent_core`)

The presence of `agent_core` changes "where patterns belong":

- `agent_labs`: show the simplest correct implementation (great for learning and labs).
- `agent_core`: implement patterns consistently so production projects get stable interfaces and operational behavior.
- `agent_lc`/`agent_lg` (optional): adapters that translate `agent_core` primitives into LangChain/LangGraph concepts; avoid putting core policies or business logic here.

### 5.1 Strategy pattern (algorithm selection)

Use when you have multiple interchangeable algorithms:
- chunking strategies (fixed, sliding, semantic)
- retrieval strategies (keyword, vector, hybrid)
- reranking strategies (none, heuristic, model-based)
- context packing strategies (strict order, budgeted, summarize-first)

### 5.2 Factory pattern (construction from config)

Use when object creation depends on environment/config and you want a single source of truth:
- provider factory (mock/ollama/openai)
- storage factory (sqlite/postgres/redis)
- vector index factory (chroma/pgvector/managed)
- telemetry exporter factory (stdout/file/otel)

Rule: one factory per component family (avoid a "god factory").

### 5.3 Registry pattern (runtime discovery + selection)

Use when you need runtime selection and/or plugin architecture:
- tool registry (already exists)
- provider registry (capability + cost + policy selection)
- retrieval registry (mode selection by intent/uncertainty/budget)

Rule: use registries only where dynamic selection matters (avoid registry sprawl).

---

## 6) Replan: How `agent_core` Affects the Roadmap

Instead of refactoring every `agent_labs` module into factories/registries, the roadmap becomes:

### Phase 0: Define boundaries (Week 0)
- Introduce `src/agent_core/` skeleton and document responsibilities.
- Decide the stable import surface for production apps (`agent_core.*`).
- Add a minimal "config -> factory" path for 1-2 components as examples.

### Phase 1: Production data + retrieval layer (Weeks 1-2)
- Implement production backends in `agent_core`:
  - Postgres storage (episodic + semantic)
  - vector index interface + at least one real backend (pgvector or Chroma persistent)
  - Redis session state (optional)
- Add context packing policy + evidence manifest in `agent_core`.
- Add memory consolidation policy in `agent_core`.

### Phase 2: Integration layer (Weeks 3-4)
- Add MCP client integration in `agent_core` (and an adapter for existing tool contracts).
- Add remote tool boundary policy: allowlists, authZ hooks, audit events.

### Phase 2.5: Ecosystem interop (optional, after Phase 0-2)
- Add `agent_lc` and `agent_lg` as optional packages (extras/optional deps).
- Add minimal adapters so projects can adopt LangChain/LangGraph without losing `agent_core` policies (audit, safety, eval, observability).
- Add one optional lab showing the mapping and tradeoffs (see Lab E).

### Phase 3: Engineering discipline (Weeks 5-6)
- Add evaluation gates (golden set runner + scorecard + CI gate).
- Add OTel exporter + trace context propagation.
- Add routing/cascade policy for multi-provider selection (cost/latency/capability).

### Phase 4: Scaling & governance (Weeks 7+)
- Multi-tenant isolation patterns across memory/retrieval/tools.
- Checkpoint/resume + idempotency utilities.
- Distributed multi-agent patterns (optional, advanced).

---

## 7) Labs (What to Add or Upgrade)

Goal: labs should teach the baseline from scratch (`agent_labs`), then show how production teams standardize and scale it (`agent_core`), and finally show how those concepts map to industry-adopted runtimes (optional LangChain/LangGraph interop).

### Lab A: Vector DB + Context + Memory Management (recommended)

**Working title:** "RAG Memory Platform Lab"  
**Goal:** an end-to-end lab combining vector retrieval, context packing, and multi-tier memory with observability + evaluation.

Exercises (progressive):
1. Ingest docs: chunk -> embed -> upsert to vector store with metadata (tenant/source/timestamp).
2. Retrieval: metadata filters -> vector search -> keyword fallback -> pack evidence with provenance.
3. Context packing policy: deterministic order + token budgets + evidence manifest.
4. Memory tiers: episodic log + semantic facts + consolidation + retention rules.
5. Observability: spans/metrics for retrieval and memory (latency, chunks included, tokens used).
6. Evaluation gate: golden set + scorecard report + regression check.

Backends to teach (selectable):
- local-first: Chroma persistent + SQLite (explicitly framed as learning/local)
- production-like: Postgres + pgvector (or managed vector DB adapter)

### Lab B: Design patterns for agents (optional, but high leverage)

Teach refactoring from hardcoded -> interface -> factory -> registry using one small workflow:
- chunking (strategy), storage (factory), tools (registry), provider (factory/registry).

### Lab C: MCP tools lab (new)

Discovery -> allowlist -> execute -> observe, with telemetry correlation and safety policies.

### Lab D: Evaluation-in-CI lab (new)

Golden set creation, stability tests (N runs), scorecard reporting, and "fail the build on regression".

### Lab E: LangChain / LangGraph interop (optional)

Goal: show how to integrate this repo's primitives into common ecosystems without coupling core code to those frameworks.

Suggested exercises:
1. LangChain: wrap one repo `ToolContract` as a LangChain Tool; demonstrate metadata/audit propagation.
2. LangChain: expose a repo retrieval pipeline as a LangChain Retriever (provenance preserved).
3. LangGraph: model a simple multi-step workflow as a graph; use a repo orchestrator step as a node; persist/restore state.

Deliverables:
- Short curriculum appendix ("Interop patterns") + one small optional lab folder + guidance on when to use `agent_core` vs framework code.

---

## 8) Current Pattern Cross-Reference (Repo Reality Check)

| Pattern | Where it exists today | Notes |
|---|---|---|
| Registry | `src/agent_labs/tools/registry.py` | strong foundation |
| Interfaces/ABCs | `src/agent_labs/llm_providers/base.py`, `src/agent_labs/memory/storage.py` | good baseline |
| Factories | ad-hoc/partial | needs consolidation and config-driven construction |

---

## 9) Next Actions (Document -> Execution)

1. Confirm the `agent_core` layering decision (scope and naming).
2. Decide which gap(s) become the first "production slice" (recommend: data + retrieval + eval gate).
3. Convert Phase 0-1 into issues/stories under space_framework governance (story -> PR -> review -> merge).

---

## 10) Proposed Progressive Learning Realignment Plan (Proposal Only)

Goal: keep this repo a learning project that (1) teaches agents from scratch and (2) evolves into industry-adopted, production-ready examples without turning the fundamentals into framework-specific code.

### 10.1 What we have today (current structure)

Truth and reference:
- `Agents/`: canonical architecture/pattern docs (truth layer).

Teaching materials:
- `curriculum/ai_agents_learning_curriculum.md`: long-form curriculum draft.
- `curriculum/presentable/`: slides/workbooks/chapters/projects packaged by level.

Hands-on:
- `labs/00`..`labs/10`: runnable labs with their own READMEs and tests.
- `src/agent_labs/`: shared educational code used by labs (framework-agnostic primitives).
- `scripts/`: interactive playground scripts that exercise `src/agent_labs/`.

### 10.2 The progressive learning model (recommended)

Define three explicit "lanes" and keep boundaries clear:

Lane A - Build from scratch (primary learning path)
- Use `Agents/` + `curriculum/presentable/` to teach concepts.
- Use `labs/` + `src/agent_labs/` to implement fundamentals (readable, minimal deps, deterministic tests).

Lane B - Productionize (platform engineering path)
- Introduce `src/agent_core/` as the stable import surface for production apps.
- Add production backends/policies/operability (storage backends, OTel export, eval gates, checkpoint/resume).
- Labs gain an "upgrade to agent_core" section (same lab, more operable implementation).

Lane C - Industry adoption (optional ecosystem interop)
- Add `src/agent_lc/` (LangChain adapters) and `src/agent_lg/` (LangGraph adapters) as optional packages.
- Teach how to map concepts, not replace them: keep policies in `agent_core`, keep adapters thin.

### 10.3 Proposed restructuring plan (no changes now)

This is a plan for incremental PRs; it does not require a large one-shot re-org.

Step 1 - Fix navigation and "single entry points"
- Make root `README.md` link to the actual curriculum entry: `curriculum/presentable/README.md`.
- Add (or update) a single lab index: `labs/README.md` with a table (Lab -> Concepts -> Curriculum chapter -> src modules).
- Add an `Agents/README.md` index to explain "truth layer" and link to the core docs.

Step 2 - Make curriculum-to-lab mapping authoritative
- Treat `curriculum/presentable/05_supporting/41_lab_integration_guide.md` as the canonical mapping table.
- Update it to include new labs (09 MCP, 10 vector/context/memory) and any future labs.
- In each chapter, add a small "Hands-on" block that points to the lab and the relevant `src/agent_labs/*` modules.

Step 3 - Standardize lab progression inside each lab folder
- Add a consistent lab template (per-lab README sections):
  - "From scratch" (use only `agent_labs`)
  - "Production upgrade" (how it would look in `agent_core`)
  - "Interop note" (optional: what LangChain/LangGraph would replace or simplify)
- Keep tests deterministic; add optional "real mode" sections for live providers/backends.

Step 4 - Clarify the role of `scripts/` as a progressive workbench
- Keep `scripts/` as the interactive playground, but add a clear mapping:
  - which script corresponds to which lab/level (beginner -> intermediate -> advanced).
- Consider consolidating Python packaging (root `pyproject.toml` vs `scripts/pyproject.toml`) to reduce setup confusion, or explicitly document why `scripts/` is its own sandbox.

Step 5 - Introduce `agent_core` in thin slices (when ready)
- Create `src/agent_core/` as the production import surface, but start small:
  - one config-driven factory example
  - one production backend example (e.g., Postgres storage or persistent vector store)
- Add one "production slice" lab that shows the delta between `agent_labs` and `agent_core`.

Step 6 - Add optional ecosystem adapters (when ready)
- Add `src/agent_lc/` and `src/agent_lg/` as optional extras (no hard dependency for the base repo).
- Add one optional lab or appendix that demonstrates the mapping and tradeoffs (not a new default learning dependency).

### 10.4 Proposed end-state structure (conceptual)

This is the intended mental model, not an instruction to move files right now:

- `Agents/` -> truth layer (architecture and patterns)
- `curriculum/presentable/` -> teaching pack (slides/workbooks/chapters/projects)
- `labs/` -> hands-on exercises (deterministic + optional real mode)
- `src/agent_labs/` -> from-scratch educational primitives
- `src/agent_core/` -> production-ready framework layer (configurable, scalable, operable)
- `src/agent_recipes/` -> composed, reusable workflows built from `agent_core`
- `src/agent_lc/` and `src/agent_lg/` -> optional adapters for LangChain/LangGraph

### 10.5 Success criteria for the realignment

You know the repo is aligned when:
- A new learner can start from one place (root README) and follow a single path end-to-end.
- Every curriculum chapter points to a lab, and every lab points back to curriculum and `src` modules.
- The repo stays runnable without LangChain/LangGraph, but has a clear "interop path" for industry adoption.
