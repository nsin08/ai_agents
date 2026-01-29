# System Overview

## Packages (distribution remains `ai_agents`)

- `agent_core` (production framework) - required
- `agent_lc` (optional LangChain integration provider)
- `agent_lg` (optional LangGraph execution engine)
- `agent_recipes` (optional templates/workflows) - parked initially, but designed for compatibility

`agent_core` does **not** import `agent_lc` or `agent_lg` on the default import path.
Optional packages register their implementations as plugins.

## High-level architecture

```mermaid
flowchart TB
  subgraph Consumers
    LIB[Library API] --> CORE
    CLI[CLI] --> CORE
    SVC[HTTP Service] --> CORE
  end

  subgraph CORE[agent_core]
    CFG[Config + Profiles] --> FCT[Factories]
    REG[Registries] --> FCT

    FCT --> ENG[ExecutionEngine]
    ENG --> POL[Policies]
    ENG --> OBS[Observability]
    ENG --> EVAL[Evaluation Gate]

    ENG --> MR[ModelRegistry]
    ENG --> TE[ToolExecutor]
    ENG --> RET[Retrieval]
    ENG --> MEM[Memory]

    TE --> TP[ToolProviders\n(MCP, native, ...)]
    RET --> VS[VectorStore]
  end

  subgraph Plugins[Optional plugins]
    LG[agent_lg\nLangGraphEngine] -.-> ENG
    LC[agent_lc\nLangChainProvider] -.-> TP
  end
```

## Core responsibilities (what makes it "production grade")

### 1) Deterministic execution mode and artifact bundles
- Every run can emit an artifact bundle (config snapshot, event log, results).
- Deterministic mode produces stable artifacts suitable for CI gates.

### 2) Tool boundary safety
- Tool contracts are explicit, versioned, and validated.
- Central enforcement point:
  - allowlists / scopes
  - risk classification (read/write/admin)
  - idempotency for write tools
  - timeouts + cancellation
  - normalized error taxonomy
  - audit-safe event emission

### 3) Multi-model roles and routing
- A run may use multiple model "roles".
- Config selects provider/model per role.
- Optional routing policy can choose between candidates later (cost/latency/health).

### 4) Observability and redaction
- Stable internal event schema.
- Exporters map events to stdout/file/memory; OTel export is optional later.
- Redaction is applied before export (PII/secrets).

### 5) Evaluation gates
- Goldens + scorecards + gate primitive to fail on regressions.
- Stability testing support for non-deterministic modes.

## Data flow (single run)

At a high level:

1. Build `AgentCore` from config (factories create registries/providers/engine).
2. Start run, create `RunContext` (run_id, trace context, tenant/user context).
3. Execute recipe/workflow via `ExecutionEngine`.
4. For each model call / tool call / retrieval:
   - emit events
   - enforce policies
   - record artifacts
5. Produce `RunResult` plus `RunArtifact` bundle.
6. Optionally evaluate against goldens; emit scorecard and gate decision.

## Deployment model (hosted product)

The hosted service is designed polling-first:
- Create run -> returns `run_id` immediately.
- Poll for run status and events.
- Streaming (SSE/WebSocket) can be added later without changing the underlying event model.

