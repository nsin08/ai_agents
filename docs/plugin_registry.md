# Plugin Registry and Entry Points

`agent_core` is built around registries of swappable components (engines, model providers, tool providers, exporters, etc.).

This document explains:
- which registries exist and what keys they use
- how plugins are discovered via Python entry points
- how to implement and register custom providers

## Registries

Registries map stable keys to constructors:

- Engines (`registry.engines`)
- Model providers (`registry.model_providers`)
- Tool providers (`registry.tool_providers`)
- Vector stores (`registry.vectorstores`)
- Exporters (`registry.exporters`)

Built-in keys are registered eagerly at import time.

Common built-in keys:
- Engines: `local`
- Model providers: `mock`, `ollama`, `openai`
- Tool providers: `native`, `mcp`, `fixture`
- Vector stores: `memory`
- Exporters: `stdout`, `file`, `memory`

## Entry point discovery

Plugins are discovered via the entry point group:

```
ai_agents.agent_core.plugins
```

A plugin is loaded only when a missing registry key is requested. This keeps optional dependencies out of the base install.

## Registering a plugin

In your plugin package's `pyproject.toml`, add:

```toml
[project.entry-points."ai_agents.agent_core.plugins"]
my_plugin = "my_pkg.agent_core_plugin:register"
```

Your `register()` function receives the `AgentCoreRegistry` instance.

## Custom model provider

A model provider must implement the `ModelClient` protocol (`agent_core.model.ModelClient`), i.e. `async generate(messages, role) -> ModelResponse`.

Example:

```python
from __future__ import annotations

from agent_core.model import ModelResponse

class MyModelProvider:
    def __init__(self, model: str, **_kwargs) -> None:
        self.model = model

    async def generate(self, messages, role):
        return ModelResponse(text=f"my-provider::{self.model}", role=role)


def register(registry) -> None:
    registry.model_providers.register("my-provider", MyModelProvider)
```

Then reference it in config:

```json
{
  "models": {"roles": {"actor": {"provider": "my-provider", "model": "example"}}}
}
```

## Custom tool provider

A tool provider must implement the `ToolProvider` protocol (`agent_core.tools.provider.ToolProvider`).

At minimum:
- `list_tools() -> list[ToolContract]`
- `execute(tool_name, arguments) -> ToolResult | Any`

Example:

```python
from __future__ import annotations

from agent_core.tools.contract import ExecutionStatus, ToolContract, ToolResult

class MyToolProvider:
    def __init__(self) -> None:
        self._contract = ToolContract(name="my_tool", description="Custom tool")

    async def list_tools(self):
        return [self._contract]

    async def execute(self, tool_name, arguments):
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"ok": True})


def register(registry) -> None:
    registry.tool_providers.register("my-tools", MyToolProvider)
```

Then enable it in config:

```json
{
  "tools": {
    "allowlist": ["my_tool"],
    "providers": {"my-tools": {}}
  }
}
```

## Notes

- If a plugin's import fails due to a missing optional dependency, `agent_core` raises a `PluginDependencyError` with an install hint.
- For a minimal test plugin, see `tests/fixtures/mock_plugin`.
