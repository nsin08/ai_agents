# AgentCore Public API

This document describes the primary entry point for `agent_core`.

## Quick start

```python
from agent_core import AgentCore, RunRequest

core = AgentCore.from_file("agent_core.json")
result = core.run_sync(RunRequest(input="Summarize this document."))
print(result.output_text)
```

## Constructors

- `AgentCore.from_file(path)`: load YAML/JSON config and build AgentCore.
- `AgentCore.from_env()`: load config from environment variables.
- `AgentCore.from_config(config)`: use a pre-built `AgentCoreConfig`.

## Execution methods

- `await core.run(request) -> RunResult`
- `await core.run_with_artifacts(request) -> (RunResult, RunArtifact)`
- `core.run_sync(request) -> RunResult` (sync wrapper)

## RunRequest + RunResult

- `RunRequest`: input text, run_id, budgets (turns/time), metadata, cancellation event.
- `RunResult`: status, output_text, turns, reason, metadata.

## Notes

- `run_sync` raises if called from an active event loop; use `await run()` in async contexts.
- Tool calls flow through `ToolExecutor` and are governed by policies.
- Observability can be disabled by setting `observability.exporter` to `disabled` (or `none`) in config.
