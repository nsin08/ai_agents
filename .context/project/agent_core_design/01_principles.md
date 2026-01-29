# Principles and Invariants

## Primary goals

1. **Production-grade by default**: safe, observable, evaluable, configurable.
2. **Determinism as a correctness gate**: offline deterministic tests and evaluation must be possible.
3. **One mental model**: regardless of provider/engine/integration choices, the same core invariants hold.
4. **Swap without rewrites**: providers and engines can be swapped via config and registries.
5. **No core coupling to external frameworks**: LangChain/LangGraph are optional packages.

## Invariants (must always hold)

### I1. Policy enforcement is centralized
- All tool calls go through a single enforcement point (`ToolExecutor`).
- Read-only, budgets, and approvals are enforced centrally, not by convention.

### I2. Observability is always emitted
- Every run produces structured events with stable correlation identifiers.
- Redaction rules are applied before exporting events.

### I3. Evaluation gates exist as code primitives
- A "gate" primitive can compare baseline vs candidate and fail the build on regressions.

### I4. No hidden side effects
- Tools declare risk (`read`/`write`/`admin`) and data-handling constraints.
- The runtime can block actions and record why.

### I5. Deterministic mode must exist
Deterministic mode means:
- No network required.
- No GPU required.
- Model responses are mocked or replayed.
- Tool providers are mocked/replayed.
- Retrieval uses fixtures or deterministic in-memory stores.

Real mode means:
- Real providers (Ollama/cloud) and real tools can be used.
- Exact-match assertions are not the primary gate; scorecards/metrics are used.

## Design constraints

### C1. Base dependencies are minimal
`agent_core` should rely only on a small set of well-understood libraries (e.g., `pydantic`, `httpx`) plus the standard library.

### C2. OpenAI support in base install
OpenAI is supported now using `httpx` (no provider SDK dependency). Other cloud providers are planned later behind the same `ModelClient` interface.

### C3. Standardization over convenience
CLI and service are wrappers over the library API and must emit the same artifact bundle format for reproducibility.

