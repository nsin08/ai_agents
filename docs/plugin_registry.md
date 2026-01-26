# Plugin Registry

This module provides registries for swappable agent_core components and an entry-point based plugin loader.

## Registries

Registries map stable keys to constructors:

- Execution engines
- Model providers
- Tool providers
- Vector stores
- Exporters

Built-in keys are registered eagerly at import time (example):

- Engines: `local`
- Model providers: `mock`, `ollama`, `openai`
- Tool providers: `native`, `mcp`
- Vector stores: `memory`

## Plugin interface

Plugins are discovered via the entry point group:

```
ai_agents.agent_core.plugins
```

Each plugin must expose a registration function with this signature:

```python
# In your plugin module

def register(registry) -> None:
    registry.engines.register("my_engine", MyEngine)
```

The loader calls `register(registry)` when the plugin key is requested.

## Example plugin (testing)

See `tests/fixtures/mock_plugin` for a minimal plugin used by unit tests.
