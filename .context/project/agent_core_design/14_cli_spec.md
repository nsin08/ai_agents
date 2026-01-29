# CLI Specification (Standardization Surface)

## Goals

- Provide a standardized way to run, evaluate, and debug across environments.
- Produce the same artifact bundle format as the service.
- Be deterministic by default when asked (no hidden network calls).

## Command name

Recommended console entry point:
- `agent-core`

## Core commands (v1)

### `agent-core run`

Runs a single request and writes artifacts.

Options (proposed):
- `--config <path>` (YAML/JSON)
- `--mode deterministic|real` (overrides config)
- `--engine <key>` (e.g., `local`, `langgraph`)
- `--artifact-dir <path>` (where to write artifact bundle)
- `--input <text>` or positional input
- `--json` (print machine-readable summary)

Exit codes:
- `0` success
- `2` policy blocked / user error (invalid config, allowlist violation)
- `3` runtime failure
- `4` evaluation gate failed (if `--gate` is used)

### `agent-core eval`

Runs an evaluation suite against a configuration and writes scorecards/gates.

Options:
- `--suite <path>` (golden suite)
- `--config <path>`
- `--mode deterministic|real`
- `--artifact-dir <path>`
- `--gate` (fail exit code on regression)

### `agent-core gate`

Compare candidate vs baseline artifacts and emit a gate decision.

Options:
- `--suite <path>`
- `--baseline <artifact_path>`
- `--candidate <artifact_path>`

### `agent-core serve`

Starts the hosted service (see `15_service_spec.md`).

Options:
- `--config <path>`
- `--host`, `--port`
- `--auth <mode>` (none/dev/token) (phase-able)

### `agent-core validate-config`

Validates a config file against schema and plugin availability.

Checks:
- schema validity
- required env vars present (without printing secrets)
- selected plugins installed (engine/provider backends)
- deterministic mode contract is satisfied (if mode deterministic)

### `agent-core plugins list`

Lists registered implementations:
- engines
- model providers
- tool providers
- vector stores
- exporters

## Output standardization

Every command should be able to output:
- human-friendly text summary
- machine-readable JSON summary (for automation)

The JSON summary must include:
- run_id
- artifact path
- status
- gate decision (if applicable)

