# Public API (Library-First)

This is the canonical API. CLI and service must be thin wrappers around it.

## Design goals

- Easy to adopt: minimal objects and good defaults.
- Async-first (network and I/O are common), with sync convenience wrappers.
- Stable types for `RunRequest`, `RunResult`, `RunArtifact`.
- Event model exists from day one (streaming can be added later).

## Proposed top-level API surface

### `AgentCore`

Responsibilities:
- Load/validate config
- Construct registries, factories, policies, providers, and engine
- Execute runs
- Produce artifacts and optional evaluation outputs

Suggested constructors:
- `AgentCore.from_env()` - load config from env and default paths
- `AgentCore.from_file(path)` - load YAML/JSON config file
- `AgentCore.from_config(config_obj)` - for programmatic embedding

Suggested methods:
- `async run(request: RunRequest) -> RunResult`
- `async run_with_artifacts(request: RunRequest) -> tuple[RunResult, RunArtifact]`
- `async run_and_evaluate(request: RunRequest, suite: GoldenSuite) -> GateDecision`

Streaming shape (future-friendly, optional v1):
- `async run_events(request: RunRequest) -> AsyncIterator[RunEvent]`
  - emits structured events, not necessarily token-by-token output

### `RunRequest`

Minimum fields:
- `input`: text or structured task spec
- `metadata`: tags/labels (optional)
- `context`: tenant/user context (optional)
- `mode`: `deterministic` | `real` (optional; can be inferred from config)

### `RunResult`

Minimum fields:
- `status`: `success` | `failed` | `canceled`
- `output_text`
- `citations` / `evidence_manifest` (if retrieval used)
- `metrics`: latency, tokens, tool calls, cost (best effort)
- `errors`: normalized errors (if failed)

### `RunArtifact`

The durable, reproducible bundle:
- config snapshot + hash
- runtime metadata (versions)
- event log (redacted)
- tool call summaries (audit safe)
- result
- evaluation results (optional)

## Sync vs Async

Recommendation:
- Implement core engine and providers as async.
- Provide a sync wrapper for convenience:
  - `AgentCore.run_sync(...)` that runs an event loop internally.

This keeps library ergonomic for:
- scripts and notebooks (sync)
- services and advanced applications (async)

## Error handling contract

Goals:
- never lose correlation IDs
- normalize errors to a small taxonomy
- preserve "why something was blocked" (policy failures)

Principles:
- policy failures are not exceptions by default; they produce a failed result with `PolicyViolation` detail.
- unexpected failures bubble up as `AgentCoreError` but also yield a partial artifact bundle when possible.

## Minimal example (import-first)

```python
from agent_core import AgentCore, RunRequest

core = AgentCore.from_file("agent_core.yaml")
result = core.run_sync(RunRequest(input="Summarize the doc"))
print(result.output_text)
```

