# Phased Delivery Plan (Implementation Order + Acceptance Criteria)

This plan assumes:
- `agent_core` is the only required production package.
- CLI and service are standardization surfaces.
- Streaming is not required in v1, but the event model is required.

## Phase 0: Core scaffolding and contracts

Deliverables:
- `agent_core` package skeleton
- registries + factories + strategies framework
- core types: RunRequest/RunResult/RunArtifact/RunEvent/RunContext
- error taxonomy
- base providers: `mock`, `ollama`, `openai` (via httpx)
- LocalEngine (minimal runtime)

Acceptance criteria:
- `pip install -e .` then `import agent_core` works with no LC/LG deps
- deterministic unit tests cover config parsing and registry behavior
- LocalEngine can run in deterministic mode end-to-end (mock model + fixture tools)

## Phase 1: Tool boundary and artifacts (make it production-shaped)

Deliverables:
- ToolContract + ToolExecutor enforcement:
  - allowlists
  - risk model
  - idempotency discipline
  - audit events
- artifact bundle writer (filesystem)
- event schema exporters (stdout/file/memory)

Acceptance criteria:
- every run produces a valid artifact bundle
- policy violations are captured as events and safe failure results
- deterministic mode never performs network I/O

## Phase 2: Retrieval slice (swappable vector store)

Deliverables:
- retrieval abstractions + evidence manifest
- vector store registry/factory
- deterministic in-memory vector store
- optional `chroma_persist` backend (if dependency allowed)

Acceptance criteria:
- evidence manifest included in artifacts and RunResult
- retrieval determinism holds under fixtures
- config swapping of vector store backend works

## Phase 3: CLI v1 (standardization)

Deliverables:
- `agent-core run`, `validate-config`, `eval`, `gate`, `serve` skeleton
- JSON output for automation

Acceptance criteria:
- CLI produces artifact bundles identical to library runs
- `validate-config` catches missing env keys and missing plugins
- `eval` produces scorecards; `gate` can fail builds

## Phase 4: Service v1 (hosted product, polling-first)

Deliverables:
- HTTP API per `15_service_spec.md`
- background worker execution
- persistent event logs + artifact downloads

Acceptance criteria:
- create run -> poll status -> poll events -> download artifacts
- service output matches CLI/library artifact formats

## Phase 5: Optional plugins (LangGraph / LangChain)

Deliverables:
- `agent_lg` provides `langgraph` engine plugin
- `agent_lc` provides `langchain` integration plugin (tools/retrieval)
- plugin loader works on-demand

Acceptance criteria:
- base install does not require LC/LG
- selecting `engine=langgraph` fails clearly if deps missing
- conformance tests ensure policies/events are preserved

## Phase 6: Streaming (optional, product UX upgrade)

Deliverables:
- SSE endpoint for events
- optional token streaming events (if desired)

Acceptance criteria:
- streamed events are identical schema to polled events
- cancellation works and emits terminal events

