# AgentCore Public API

This document describes the public interface for `agent_core`.

If you are new, start with the CLI quick start in the repository README, then come back here for the API contracts.

## AgentCore

`AgentCore` is the primary entry point for running a single agent execution.

### Constructors

- `AgentCore.from_file(path)`: load JSON/YAML config from a file.
- `AgentCore.from_env()`: load config from environment variables (prefix `AGENT_CORE_`).
- `AgentCore.from_config(config)`: build from an `AgentCoreConfig` instance.

### Execution

- `await core.run(request) -> RunResult`
- `await core.run_with_artifacts(request) -> (RunResult, RunArtifact)`
- `core.run_sync(request) -> RunResult` (sync wrapper; raises if called inside an event loop)

`run_with_artifacts` writes a run bundle to the configured artifact store (default: local filesystem).

## RunRequest

A request to execute a run.

Fields (see `agent_core.engine.RunRequest`):
- `input` (str): user input prompt.
- `run_id` (str): caller-provided or auto-generated run id.
- `max_turns` (int): max state-machine turns.
- `timeout_s` (float | None): per-run timeout.
- `metadata` (dict): arbitrary metadata.
- `cancel_event` (asyncio.Event | None): cooperative cancellation.

Example:

```python
from agent_core import AgentCore, RunRequest

core = AgentCore.from_file("examples/configs/mock.json")
result = await core.run(RunRequest(input="hello", max_turns=3))
print(result.status, result.output_text)
```

## RunResult

The outcome of a run.

Fields (see `agent_core.engine.RunResult`):
- `status`: `success`, `failed`, `timeout`, `budget_exceeded`, `cancelled`
- `output_text`: final answer text (best effort)
- `turns`: number of turns executed
- `reason`: optional reason code
- `metadata`: extra run metadata

## RunArtifact

`RunArtifact` is the index for a saved run bundle.

Fields (see `agent_core.artifacts.models.RunArtifact`):
- `run_id`, `status`, `started_at`, `finished_at`
- `config_hash` (sha256 of redacted config snapshot)
- `paths` (relative paths inside the run directory)
- `versions` (package version, optional git commit)
- `result` (status/output_text)
- `error` (if failed)

Bundle contents (default filesystem store):
- `config.snapshot.json`
- `events.jsonl`
- `tool_calls.json`
- `run.json`

Example:

```python
from agent_core import AgentCore, RunRequest

core = AgentCore.from_file("examples/configs/mock.json")
result, artifact = await core.run_with_artifacts(RunRequest(input="hello"))
print(artifact.run_id)
```

## Notes

- Tool calls flow through `ToolExecutor` and are governed by config policies and allowlists.
- Observability can be disabled by setting `observability.exporter` to `disabled`.
- For configuration details and examples, see `docs/configuration.md`.
