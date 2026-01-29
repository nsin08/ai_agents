# Agent Core System Design (Production Framework)

**Date:** 2026-01-25  
**Scope:** `agent_core` (production framework), plus optional packages `agent_lc`, `agent_lg`, and `agent_recipes`  
**Constraint:** This design pack does **not** reference learning code. It is written as a standalone production architecture.

## What we are building

`agent_core` is a **single, production-ready, importable framework** that developers can install and use immediately, with:
- Deterministic correctness gates (tests + evaluation).
- A strict, auditable tool boundary (policy enforcement + validation + idempotency + error taxonomy).
- Multi-model role support (router/planner/actor/critic/summarizer/embedder).
- Pluggable swap points via **registries + factories + strategies**:
  - LLM providers (mock/ollama/openai now; others later)
  - Orchestration engine (built-in LocalEngine; optional LangGraph engine via `agent_lg`)
  - Integration ecosystem (native providers; optional LangChain provider via `agent_lc`)
  - Retrieval/vector store backends, tool providers (including MCP), exporters, scorers

Consumption surfaces (standardized):
- Library API (canonical)
- CLI (canonical wrapper over the library)
- Hosted service (canonical wrapper over the library; polling-first, streaming later)

## Non-goals (v1)

- Token streaming as a hard requirement (we design an event model that can be streamed later).
- Shipping a full managed platform (billing/UI/enterprise IAM).
- Coupling core to LangChain or LangGraph.

## Document map

1. `01_principles.md` - goals, invariants, determinism contract
2. `02_system_overview.md` - component model, layering, data flow
3. `03_public_api.md` - canonical library API (sync/async, run + run_stream later)
4. `04_configuration.md` - config model, multi-role models, env/file layering
5. `05_plugin_architecture.md` - registries/factories/strategies, plugin discovery
6. `06_runtime_engines.md` - LocalEngine semantics; LangGraph engine integration point
7. `07_model_layer.md` - model clients, roles, routing policy; OpenAI via `httpx`
8. `08_tool_boundary.md` - ToolContract, ToolExecutor, MCP provider, audit, idempotency
9. `09_retrieval_layer.md` - retrieval strategies, evidence manifest, vector stores
10. `10_memory_layer.md` - session/long-term/run state stores, policies
11. `11_observability.md` - event schema, trace context, exporters, redaction
12. `12_evaluation_gates.md` - goldens, scorecards, gates, CI usage
13. `13_artifacts_and_run_state.md` - run artifacts bundle, persistence, replay
14. `14_cli_spec.md` - commands, outputs, determinism modes
15. `15_service_spec.md` - HTTP API, polling model, auth, deployment notes
16. `16_security_and_compliance.md` - threat model + controls
17. `17_phased_delivery_plan.md` - implementation phases and acceptance criteria
18. `18_consumption_surfaces.md` - library/CLI/service/web/VSCode integration model
19. `19_error_taxonomy.md` - stable error categories and mappings
20. `20_operations.md` - versioning, SLOs, deployment, governance

Schemas/specs:
- `schemas/agent_core_config.schema.json`
- `schemas/run_event.schema.json`
- `schemas/run_artifact.schema.json`
- `specs/openapi.v1.yaml` (service API)

ADRs:
- `adrs/README.md` (index)
