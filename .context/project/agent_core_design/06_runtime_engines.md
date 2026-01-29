# Runtime Engines (ExecutionEngine)

## What an engine is

An `ExecutionEngine` is the runtime that executes a run:
- it coordinates model calls, retrieval, tools, memory, and policies
- it produces events and artifacts
- it supports cancellation and timeouts

Engines are swappable via the engine registry:
- built-in: `local`
- optional plugin: `langgraph` (via `agent_lg`)
- future: other workflow engines

## Engine interface (conceptual)

Minimal responsibilities:
- `run(request, components) -> RunResult` (async)
- `run_with_artifacts(...) -> (RunResult, RunArtifact)` (async)
- optional: `run_events(...) -> AsyncIterator[RunEvent]` (later)

The engine must not:
- execute tools directly (must call `ToolExecutor`)
- emit raw/unsafe data (must use observability layer + redaction)

## LocalEngine (built-in, deterministic reference)

LocalEngine is the canonical reference engine:
- minimal dependencies
- predictable semantics
- easy to test deterministically

### Suggested step model (linear v1)

1. Initialize `RunContext` and budgets.
2. (Optional) `router` role: classify request and set retrieval gating.
3. (Optional) Retrieval + context packing: produce evidence manifest.
4. `planner` role: produce a plan (structured).
5. `actor` role: propose tool calls or produce answer.
6. Tool execution: `ToolExecutor.execute(...)` for each call (policy enforced).
7. `critic` role: verify or request retries (bounded by budgets).
8. `summarizer` role: finalize response formatting (optional).
9. Produce `RunResult` + artifacts.

### Determinism requirements

In deterministic mode:
- model clients must be mock/replay
- tool providers must be mock/replay
- retrieval must be fixture-based or deterministic
- event ordering should be stable (within documented constraints)

## LangGraphEngine (optional via `agent_lg`)

LangGraphEngine is an alternative runtime for:
- branching flows
- long-running workflows
- checkpoint/resume semantics
- HITL approvals

### Key requirement

LangGraphEngine must preserve core invariants:
- tool calls still go through `ToolExecutor`
- policies are enforced in core
- events follow the core schema and correlation IDs

### Checkpoint/resume model

`agent_core` defines a `RunState` schema and a `RunStore` interface.

LangGraphEngine:
- uses LangGraph checkpointing
- maps checkpoint state to the core `RunState` representation
- records enough to resume safely and deterministically where feasible

## Timeouts and cancellation

Timeouts must exist at three levels:
- model call timeouts (per role)
- tool call timeouts (per tool/provider)
- run-level budget (max time, max tool calls, max tokens)

Cancellation must:
- stop new steps from starting
- best-effort cancel in-flight tool/model calls
- emit terminal events and artifact bundle

