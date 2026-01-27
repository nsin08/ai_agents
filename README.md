# AI Agents — Knowledge Base + Learning Program (Monorepo)

This repository is an evolving monorepo for learning, building, and teaching **AI agent systems** from fundamentals to production architecture. It is intentionally structured so that:

- An individual contributor can learn by doing (theory → labs → projects → reflection).
- A team can reuse the same material for internal enablement (slides, workbooks, exercises, and project rubrics).
- The same concepts can be taught at different depths (freshers → engineers → architects → leaders) without rewriting the underlying “truth layer.”

In short: `Agents/` captures the canonical architecture patterns and engineering practices; the curriculum repackages that knowledge for different audiences; and the labs/projects turn it into hands-on, verifiable experience (including testing, safety, observability, and operations).

## Goals

1) **Comprehensive knowledge base (truth layer)**
- Maintain a production-oriented reference for agent architecture and engineering practices.
- First iteration prioritizes closing gaps identified in the critical review (testing/eval, security, failure handling, cost engineering, operations).

2) **Modular learning program (audience-specific paths)**
- Provide presentation-ready curriculum material that can be assembled into tailored paths for:
  - College freshers
  - Mid-level engineers (builders)
  - Architects (systems designers)
  - Leaders (strategy/operating model)

3) **Runnable labs (shared core + many lab folders)**
- Build a Python lab library that starts framework-agnostic (control loop, tool contracts, memory, safety) and later explores frameworks (LangChain/LangGraph) without rewriting the fundamentals.
- Every lab supports two modes:
  - **Real LLM mode:** local Ollama when available; cloud vendors when configured
  - **Deterministic test mode:** mocked LLM for reproducible tests and CI

## Scope (What This Repo Intends To Cover)

### A) Reference Knowledge Base (Truth Layer)

The `Agents/` directory is the canonical source-of-truth for agent architecture and engineering patterns. It aims to be directly usable for designing and building real systems (not just “prompting tips”).

Focus areas include:
- Agent definition and autonomy spectrum
- Control loop orchestration and state management
- Tool design (schemas, permissions, side effects, idempotency)
- Memory systems (RAG, short-term, long-term) with write/retrieval policies
- Context engineering (packing, budgets, provenance/citations)
- Guardrails and policies (risk tiers, approvals, enforcement points)
- Observability (logs/metrics/traces) and cost attribution
- Scalability and performance patterns
- Case studies and reference architectures (support/coding/medical/ops)

### B) Critical Review → Iteration Goals

The `.context/review/` folder captures gaps and improvement areas discovered while reviewing the reference docs. The first “knowledge base iteration” focuses on shipping concrete, reusable artifacts (not just prose):

- Failure modes and recovery patterns (taxonomy + mitigation matrix)
- Testing and evaluation framework (golden/adversarial/regression + release gates)
- Security and compliance (threat model + controls + checklists)
- Cost engineering (instrumentation, attribution, optimization playbook)
- Production operations (versioning, deployment, rollback, SLOs, runbooks)

### C) Modular Learning Program (Audience-Specific Paths)

The learning program is modular and designed to be assembled into tailored paths for different audiences. The same underlying modules are reused, but depth and deliverables change by audience (e.g., “build it” vs “design it” vs “fund/govern it”).

### D) Runnable Labs (Python, Framework-Agnostic First)

Labs are the hands-on companion to the knowledge base and curriculum:
- Start with a minimal, readable, framework-agnostic implementation of agent fundamentals.
- Add “industry standard” patterns via evaluation, safety, observability, and operational readiness.
- Introduce framework examples later as an additional layer, not as the foundation.

## Non-Goals (for now)

- Shipping a production agent platform as a deployable product
- Locking the repo to a single vendor or framework as “the one way”

## Repository Structure (Current)

- `Agents/` — Canonical reference documents (the truth layer)
- `.context/review/` — Critical review notes and identified gaps
- `curriculum/presentable/` — Presentation-ready curriculum, organized by level + projects
  - `00_overview/`, `01_beginner/`, `02_intermediate/`, `03_advanced/`, `04_pro/`
  - `projects/` — Project specs (P01–P12)
  - `90_supporting/` — Glossary and mappings
- `chapters/`, `curriculum/` — Additional/legacy structure (in progress)

## Agent Core Docs

- AgentCore public API: `docs/agent_core_api.md`
- Observability & run events: `docs/observability.md`
- Execution engines: `docs/engine.md`
- Tool contracts and executor: `docs/tools.md`
- Short-term memory: `docs/memory.md`

Quick start (AgentCore):
```python
from agent_core import AgentCore, RunRequest

core = AgentCore.from_file("agent_core.json")
result = core.run_sync(RunRequest(input="Hello"))
print(result.output_text)
```
Note: `run_sync` raises if called inside an active event loop; use `await core.run(...)` in async contexts.

Example (short-term session memory):
```python
import asyncio

from agent_core.memory import InMemorySessionStore


async def main() -> None:
    store = InMemorySessionStore(max_tokens=200)
    await store.add_message("user", "Hello")
    context = await store.get_context()
    print(context)


asyncio.run(main())
```


## Labs Architecture (Planned)

### Shared Core: `src/agent_labs/`

The shared core prevents duplicated plumbing across labs and keeps the lab suite maintainable as it grows. The goal is a small, readable, framework-agnostic reference implementation of an agent system.

Expected submodules (subject to iteration):
- `src/agent_labs/providers/` — LLM provider adapters (`mock`, `ollama`, later `openai`/others) behind one interface
- `src/agent_labs/controller/` — Observe/Plan/Act/Verify loop + state + stop conditions
- `src/agent_labs/tools/` — tool contracts, schema validation, permissions, idempotency helpers
- `src/agent_labs/memory/` — session state + long-term memory hooks + write/retrieval policies
- `src/agent_labs/context/` — context packing utilities, token budgeting, provenance formatting
- `src/agent_labs/observability/` — structured events/logging + minimal metrics
- `src/agent_labs/eval/` — golden test runner, regression comparison, report outputs
- `src/agent_labs/safety/` — guardrails, approval gates, and enforcement helpers

### Lab Modules: `labs/`

Each lab is a small runnable module that focuses on one capability and is usable as training material.

Typical lab contents:
- `README.md` — concept overview, prerequisites, how to run
- `exercise.md` — tasks + expected outputs
- `src/` — runnable code for the lab
- `tests/` — deterministic tests (mock LLM)

Suggested high-level modules:
- `labs/00/` - environment checks and setup
- `labs/01/` - RAG fundamentals (retrieval + citations)
- `labs/02/` - tool integration (schemas, validation, side effects)
- `labs/03/` - orchestrator patterns (agent loop)
- `labs/04/` - memory management (tiers, persistence basics)
- `labs/05/` - context engineering (packing, budgets, compression)
- `labs/06/` - observability and monitoring (logs/metrics/traces)
- `labs/07/` - safety and guardrails
- `labs/08/` - multi-agent systems
- `labs/09/` - MCP tool servers (offline foundations)
- `labs/10/` - vector retrieval + context packing + memory management (offline foundations)

## Curriculum Entry Point

Start here:
- `curriculum/presentable/README.md`
- `labs/README.md` (Lane A lab index)

## Labs Configuration (Planned)

Labs will be configurable via environment variables to support local and cloud execution:

- `LLM_PROVIDER=mock|ollama|openai|...`
- `LLM_MODEL=...`
- `LLM_BASE_URL=...` (e.g., Ollama)
- Provider keys (e.g., `OPENAI_API_KEY=...`)

## Cross-Platform Support

The repo targets:
- Windows (PowerShell + WSL-friendly)
- macOS
- Linux

## Status

- Knowledge base: in progress
- Critical gaps: tracked in `.context/review/`
- Presentable curriculum: scaffolded and actively refined
- Labs: planned (Python 3.11, `uv`, local-first; deterministic mock mode for CI)

## Key Decisions (and Why)

This repository is intended to evolve over time, but a few foundational choices are intentionally “locked” early to keep the monorepo coherent and maintainable.

### Python 3.11

Selected to maximize ecosystem compatibility across common agent/RAG tooling while still being modern and performant. This reduces onboarding and dependency friction for peers.

### `uv` for dependencies

Selected for speed and simplicity in a monorepo context. The goal is reproducible installs and fast iteration without introducing heavy project-management overhead.

### One shared core + many lab folders (Option A)

Selected to avoid duplicated “plumbing” across labs. A shared core (`src/agent_labs/`) keeps concepts consistent (controller/tool contracts/memory/safety) and makes long-term maintenance realistic as the number of labs grows.

### Framework-agnostic first, frameworks later

Selected to ensure learners internalize the fundamentals (control loop, contracts, safety, evaluation) independent of any particular framework. LangChain/LangGraph are treated as optional implementations of patterns, not the patterns themselves.

### Two execution modes for every lab

- **Real LLM mode:** for hands-on realism and practical demos (local Ollama when available; cloud vendors when configured).
- **Deterministic test mode:** for repeatable learning, CI reliability, and regression testing (mocked LLM, no network requirement).

This prevents labs from becoming flaky or vendor-dependent while still supporting “real world” experimentation.

### Local-first, devcontainer as a staged enhancement

Selected to minimize initial setup friction (especially across Windows/macOS/Linux). An optional devcontainer can be added later as a “stage 2” onboarding improvement once the first labs stabilize.

### Vendor/config strategy (Ollama → cloud)

Selected to keep local iteration cheap and fast while preserving a path to production-like testing. Providers are configured via env vars (see “Labs Configuration”), and implemented behind a single interface in `src/agent_labs/providers/`.
