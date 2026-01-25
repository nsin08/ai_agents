# Plugin Registry System

A generic, extensible plugin system for AI Agents with entry point discovery and lazy loading.

## Features

- **Generic Registry Base Class**: Extend for any plugin type (tools, models, engines, exporters)
- **Entry Point Discovery**: Automatic plugin discovery using setuptools entry points
- **Lazy Loading**: Plugins loaded on first access for optimal performance
- **Lifecycle Management**: Load, reload, and unload plugins at runtime
- **Metadata Tracking**: Version, dependencies, author, and tags for each plugin
- **Python 3.11+**: Modern type hints and async support

## Quick Start

### 1. Create a Registry

```python
from agent_labs.registry import Registry, discover_plugins

class ToolRegistry(Registry):
    """Registry for agent tools."""
    plugin_type = "agent_labs.tools"

registry = ToolRegistry()
```

### 2. Discover Plugins

Plugins are discovered from setuptools entry points:

```python
# Auto-discover from entry points
count = discover_plugins(registry, lazy=True)
print(f"Discovered {count} plugins")
```

### 3. Use Plugins

```python
# Get a plugin (lazy loads on first access)
tool = registry.get("my_tool")

# Check metadata without loading
metadata = registry.get_metadata("my_tool")
print(f"{metadata.name} v{metadata.version}")

# List all plugins
plugins = registry.list_plugins()
print(f"Available: {plugins}")
```

## Plugin Types

### Tools

```toml
# pyproject.toml
[project.entry-points."agent_labs.tools"]
my_tool = "my_package.tools:MyTool"
```

### Models

```toml
[project.entry-points."agent_labs.models"]
my_provider = "my_package.providers:MyProvider"
```

### Engines

```toml
[project.entry-points."agent_labs.engines"]
my_engine = "my_package.engines:MyEngine"
```

### Exporters

```toml
[project.entry-points."agent_labs.exporters"]
my_exporter = "my_package.exporters:MyExporter"
```

## Architecture

```
registry/
├── __init__.py       # Public API exports
├── base.py           # Registry base class + PluginMetadata
├── loader.py         # Entry point discovery
└── README.md         # This file
```

### Core Components

1. **Registry**: Abstract base class for plugin management
   - Registration and retrieval
   - Lazy loading support
   - Lifecycle management (reload, unregister)
   
2. **PluginLoader**: Base interface for loading plugins
   - `EntryPointLoader`: Discovers plugins from setuptools entry points
   - Extensible for custom loaders (file system, remote, etc.)

3. **PluginMetadata**: Plugin information
   - Name, version, description
   - Author, dependencies, tags
   - Entry point reference

4. **PluginInfo**: Runtime plugin state
   - Metadata reference
   - Plugin class and instance
   - Load status and lazy loader

## API Reference

### Registry

```python
class Registry(ABC):
    """Generic plugin registry."""
    
    plugin_type: Optional[str] = None  # Override in subclass
    
    def register(self, name: str, plugin_class: Type, 
                 metadata: Optional[PluginMetadata] = None,
                 lazy: bool = True, **init_kwargs) -> None:
        """Register a plugin."""
    
    def get(self, name: str, load: bool = True) -> Optional[Any]:
        """Get plugin by name, loading if necessary."""
    
    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata without loading."""
    
    def list_plugins(self, loaded_only: bool = False) -> List[str]:
        """List registered plugin names."""
    
    def is_loaded(self, name: str) -> bool:
        """Check if plugin is loaded."""
    
    def reload(self, name: str) -> bool:
        """Reload plugin (creates new instance)."""
    
    def unregister(self, name: str) -> bool:
        """Remove plugin from registry."""
    
    def clear(self) -> None:
        """Remove all plugins."""
```

### EntryPointLoader

```python
class EntryPointLoader(PluginLoader):
    """Load plugins from setuptools entry points."""
    
    def __init__(self, group: str, lazy: bool = True):
        """Initialize loader with entry point group."""
    
    def discover_entry_points(self) -> List[EntryPoint]:
        """Find all entry points in group."""
    
    def load_plugins(self, registry: Registry) -> int:
        """Load all plugins into registry. Returns count."""
```

### Convenience Functions

```python
def discover_plugins(registry: Registry, lazy: bool = True) -> int:
    """
    Auto-discover and load plugins for a registry.
    Registry must have plugin_type defined.
    """
```

## Examples

### Basic Usage

```python
from agent_labs.registry import Registry, discover_plugins

class ToolRegistry(Registry):
    plugin_type = "agent_labs.tools"

registry = ToolRegistry()
count = discover_plugins(registry)

# List and use plugins
for name in registry.list_plugins():
    tool = registry.get(name)
    print(f"Loaded: {name}")
```

### Manual Registration

```python
class MyPlugin:
    __version__ = "1.0.0"
    
    def execute(self):
        return "result"

registry = ToolRegistry()
registry.register("my_plugin", MyPlugin, lazy=True)

# Use plugin
plugin = registry.get("my_plugin")
result = plugin.execute()
```

### Custom Metadata

```python
from agent_labs.registry import PluginMetadata

metadata = PluginMetadata(
    name="custom_plugin",
    version="2.0.0",
    description="A custom plugin",
    author="Me",
    dependencies=["httpx>=0.24.0"],
    tags=["utility", "data"]
)

registry.register("custom", MyPlugin, metadata=metadata)
```

### Lifecycle Management

```python
# Load plugin
tool = registry.get("my_tool")

# Check if loaded
if registry.is_loaded("my_tool"):
    print("Plugin is active")

# Reload (creates new instance)
registry.reload("my_tool")

# Unregister
registry.unregister("my_tool")
```

## Testing

```bash
# Run all registry tests
pytest tests/unit/registry/ tests/integration/test_plugin_integration.py -v

# Run specific test file
pytest tests/unit/registry/test_plugin_registry.py -v

# Run with coverage
pytest tests/unit/registry/ --cov=src/agent_labs/registry --cov-report=term-missing
```

## Best Practices

### 1. Define Plugin Type

Always set `plugin_type` for entry point discovery:

```python
class MyRegistry(Registry):
    plugin_type = "my_app.plugins"  # Must match entry point group
```

### 2. Use Lazy Loading

Default to lazy loading for better performance:

```python
registry.register("heavy_plugin", HeavyPlugin, lazy=True)
```

### 3. Include Metadata

Add version and dependencies to plugin classes:

```python
class MyPlugin:
    __version__ = "1.0.0"
    __dependencies__ = ["dep1>=1.0"]
    __author__ = "Your Name"
```

### 4. Handle Errors

Wrap plugin loading in try-catch:

```python
try:
    plugin = registry.get("my_plugin")
except Exception as e:
    logger.error(f"Failed to load plugin: {e}")
```

### 5. Test Plugins Independently

Create isolated tests for each plugin:

```python
def test_my_plugin():
    plugin = MyPlugin()
    result = plugin.execute()
    assert result is not None
```

## Extending the System

### Custom Loaders

Create loaders for different plugin sources:

```python
from agent_labs.registry import PluginLoader

class FileSystemLoader(PluginLoader):
    """Load plugins from a directory."""
    
    def load_plugins(self, registry: Registry) -> int:
        # Scan directory
        # Import and register plugins
        # Return count
        pass
```

### Specialized Registries

Extend Registry for domain-specific needs:

```python
class ModelRegistry(Registry):
    plugin_type = "agent_labs.models"
    
    def get_provider(self, name: str, **config):
        """Get configured provider instance."""
        provider_class = self.get(name, load=False)
        return provider_class(**config) if provider_class else None
```

## Documentation

- [Plugin Development Guide](../plugin_development.md) - How to create plugins
- [Examples](../examples/plugin_registry_examples.py) - Usage examples
- [API Tests](../../tests/unit/registry/) - Test suite as documentation

## Related

- `agent_labs.tools` - Tool plugin implementations
- `agent_labs.llm_providers` - Model provider plugins
- `agent_labs.config` - Configuration system
