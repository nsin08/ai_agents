# Testing Guide

## Deterministic tests

Deterministic tests use:

- `MockProvider` for model calls
- `FixtureToolProvider` for tool execution

This keeps CI stable without network/GPU dependencies.

## Mock responses

Store mock model responses in `tests/fixtures/mock_responses.json` as a list of strings.
`MockProvider` selects a response based on the prompt hash + seed.

## Tool fixtures

Store tool fixtures in `tests/fixtures/tool_fixtures.json` as a list of entries:

```json
{
  "tool_name": "calculator",
  "tool_version": "1.0",
  "args_hash": "<sha256 hash of args>",
  "result": {"value": 4}
}
```

Use `agent_core.providers.hash_args` to compute the args hash.

## Example deterministic config

```python
from agent_core.config.models import AgentCoreConfig, ModelSpec, ModelsConfig, ToolsConfig

config = AgentCoreConfig(
    mode="deterministic",
    models=ModelsConfig(roles={"actor": ModelSpec(provider="mock", model="deterministic")}),
    tools=ToolsConfig(providers={"fixture": {"path": "tests/fixtures/tool_fixtures.json"}}),
)
```
