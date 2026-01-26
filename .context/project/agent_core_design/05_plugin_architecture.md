# Plugin Architecture (Registries, Factories, Strategies)

## Goal

Enable swapping components (engines, integrations, providers, backends) without:
- rewriting application code
- coupling `agent_core` to optional ecosystems (LangChain/LangGraph)

## Core patterns

### Registry pattern (runtime selection)

Use registries where runtime selection is needed:
- execution engines
- model providers
- tool providers
- vector store backends
- exporters
- evaluation scorers

A registry maps a stable key -> constructor/factory:
- `local`
- `openai`
- `ollama`
- `mcp`
- `langgraph` (optional)
- `langchain` (optional)

### Factory pattern (config-driven construction)

Factories build runtime objects from config:
- `EngineFactory` reads `config.engine` -> returns an `ExecutionEngine`.
- `ModelFactory` reads `config.models.roles.*` -> returns `ModelRegistry`.
- `ToolProviderFactory` reads `config.tools.*` -> returns provider instances.

Factories should:
- validate required config fields
- fail fast with actionable errors
- attach build metadata (for artifacts)

### Strategy pattern (algorithm selection)

Use strategies for algorithmic choices:
- retrieval strategy (vector-only / hybrid / rerank)
- context packing strategy
- routing strategy (model selection) (later)

Strategies are selected by key and have structured config.

## Plugin loading (optional packages)

### Design constraint

`agent_core` must not import optional packages on the default import path.
Plugins must be loaded only when requested by config or API.

### Recommended mechanism: entry points (on-demand)

Use `importlib.metadata.entry_points()` to discover plugins by key.

Proposed entry point group:
- `ai_agents.agent_core.plugins`

Each plugin exposes a function:
- `register(registry: AgentCoreRegistry) -> None`

`agent_core` provides a plugin loader:
- `load_plugin(key: str) -> None`
  - imports only the plugin corresponding to `key`
  - plugin then registers its implementations (engine/provider/etc.)

### Dependency handling

Because entry points are not conditional on extras, a plugin may exist even if its third-party deps are not installed.

Rule:
- Loading a plugin that requires missing deps must fail with a clear message:
  - "Install `ai_agents[langgraph]` to enable `langgraph` engine."
- Plugins should avoid importing heavy deps at module import time if possible; defer until `register(...)` or later.

### Built-in vs plugin-provided implementations

Registries should have built-ins registered eagerly:
- `local` engine
- `mock`, `ollama`, `openai` model providers (base)
- `native` tool provider and `mcp` provider (base)
- `memory` vector store (deterministic)
- basic exporters (stdout/file/memory)

Optional implementations are registered only when loaded:
- `langgraph` engine
- `langchain` integration provider
- `chroma_persist` vector store (if treated as optional dependency)

## Conformance tests (non-negotiable)

Any `ExecutionEngine` implementation must pass a conformance suite:
- deterministic mode produces the same `RunResult` and event invariants
- policies are enforced identically
- tool calls cannot bypass `ToolExecutor`
- observability event schema is adhered to

This is how "swappable" stays safe.

