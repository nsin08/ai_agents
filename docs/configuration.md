# AgentCore Configuration Guide

This guide documents the `agent_core` configuration model, how configuration is loaded, and provides example configs.

## Quick Start

Create a minimal config file (JSON):

```json
{
  "engine": {"key": "local", "config": {}},
  "mode": "real",
  "models": {
    "roles": {
      "actor": {"provider": "mock", "model": "deterministic"}
    }
  },
  "tools": {"allowlist": [], "providers": {}},
  "observability": {"exporter": "stdout"},
  "artifacts": {"store": {"backend": "filesystem", "config": {"base_dir": "artifacts"}}}
}
```

Run:

```bash
agent-core run "hello" --config examples/configs/mock.json
```

Notes:
- YAML is supported only if `PyYAML` is installed.
- Tools are deny-by-default. If you want tools, set a non-empty `tools.allowlist`.

## Configuration Precedence

`agent_core.config.load_config()` merges sources in this order (last wins):

1) Defaults (the `AgentCoreConfig()` model defaults)
2) File config (JSON/YAML)
3) Environment variables (prefix `AGENT_CORE_`)
4) Explicit overrides (used by CLI)

## Environment Variable Mapping

Environment variables are mapped into the config using:

- Prefix: `AGENT_CORE_`
- Nesting: `__` (double underscore)
- Lowercased keys (e.g. `AGENT_CORE_MODE=deterministic` -> `mode`)

Examples:

```bash
# Equivalent to config.mode = "deterministic"
AGENT_CORE_MODE=deterministic

# Equivalent to config.artifacts.store.config.base_dir = "out"
AGENT_CORE_ARTIFACTS__STORE__CONFIG__BASE_DIR=out

# Equivalent to config.observability.exporter = "stdout"
AGENT_CORE_OBSERVABILITY__EXPORTER=stdout
```

## Schema Sections (AgentCoreConfig)

Top-level sections:

- `app`: name, environment
- `mode`: `real` or `deterministic`
- `engine`: engine key + config
- `models`: role -> model spec
- `tools`: tool allowlist + provider configs
- `retrieval`: vector store backend (Phase 1: memory)
- `memory`: session store backend (Phase 1: memory)
- `policies`: read-only and budgets
- `observability`: exporter + redaction
- `evaluation`: evaluation gate settings (Phase 1: mostly disabled)
- `artifacts`: artifact store backend (Phase 1: filesystem)
- `service`: service settings (Phase 1: disabled)

## Models and Roles

`models.roles` is a map of role name -> `ModelSpec`.

Common roles used by `LocalEngine`:
- `planner`: produces a plan (falls back to `actor` if missing)
- `actor`: produces tool calls and the final answer
- `critic`: optional verifier (if present, controls stop condition)

Example:

```json
{
  "models": {
    "roles": {
      "planner": {"provider": "mock", "model": "deterministic"},
      "actor": {"provider": "mock", "model": "deterministic"}
    }
  }
}
```

## Tools (Allowlist and Providers)

Tools are deny-by-default.

- If `tools.allowlist` is empty, all tool calls are blocked.
- To enable tools, set `tools.allowlist` to the tool names you want to permit.

Example (enable calculator):

```json
{
  "tools": {
    "allowlist": ["calculator"],
    "providers": {}
  }
}
```

Tool providers:
- `native`: built-in tools (calculator, web_search, file_read)
- `mcp`: MCP-backed tools
- `fixture`: deterministic replay from a fixture file

## Deterministic Mode

Deterministic mode is intended for CI-like runs (no network) and stable artifacts.

Requirements (enforced by `AgentCoreConfig.validate_deterministic()`):
- All models must use `provider=mock`
- A fixture tool provider must be configured: `tools.providers.fixture.path`

Example:

```json
{
  "mode": "deterministic",
  "models": {"roles": {"actor": {"provider": "mock", "model": "deterministic"}}},
  "tools": {
    "allowlist": ["calculator"],
    "providers": {"fixture": {"path": "tests/fixtures/tool_fixtures.json"}}
  }
}
```

## Example Configs

See `examples/configs/`:
- `mock.json` (quick start)
- `deterministic.json`
- `ollama.json`
- `openai.json`

## Related Docs

- `docs/agent_core_api.md`
- `docs/engine.md`
- `docs/tools.md`
- `docs/observability.md`
- `docs/artifacts.md`
- `docs/performance.md`
- `docs/plugin_registry.md`
