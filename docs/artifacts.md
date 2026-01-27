# Run Artifacts & Deterministic Mode

This document describes the run artifact bundle and deterministic mode usage.

## Artifact bundle (v1)

A run artifact bundle is a directory containing:

```
run/
  run.json
  config.snapshot.json
  events.jsonl
  tool_calls.json
```

### `run.json` fields
- `run_id`, `status`, `started_at`, `finished_at`
- `config_hash`
- `paths` to bundle files
- `versions` (best-effort)
- `result` summary

### `config.snapshot.json`

Resolved config with secrets/PII redacted.

### `events.jsonl`

Redacted run events as JSONL (one event per line).

### `tool_calls.json`

Audit-safe tool call summaries (redacted).

## Deterministic mode

Deterministic mode ensures repeatable results and artifacts when using mock
providers and fixture tools.

Example config:

```json
{
  "mode": "deterministic",
  "models": { "roles": { "actor": { "provider": "mock", "model": "deterministic" } } },
  "tools": { "providers": { "fixture": { "path": "tests/fixtures/tool_fixtures.json" } } }
}
```

Use `AgentCore.run_with_artifacts(...)` to produce a bundle. For repeatability in
tests, provide a stable `run_id` in `RunRequest`.
