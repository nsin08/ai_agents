# Plugin Development Guide

## Overview

The Agent Labs plugin system allows you to extend core functionality without modifying the codebase. This guide explains how to create and register plugins for tools, models, engines, and exporters.

## Plugin System Architecture

The plugin system consists of:

1. **Registry**: Generic base class for managing plugins
2. **Entry Points**: Setuptools mechanism for plugin discovery
3. **Lazy Loading**: Plugins are loaded only when accessed
4. **Metadata**: Version, dependencies, and description tracking

## Creating a Plugin

### 1. Define Your Plugin Class

Create a plugin class that implements the required interface for your plugin type:

```python
class MyCustomTool:
    """My custom tool for data processing."""
    
    # Optional: Define metadata as class attributes
    __version__ = "1.0.0"
    __author__ = "Your Name"
    __dependencies__ = ["httpx>=0.24.0", "pydantic>=2.0"]
    __tags__ = ["data", "processing"]
    
    def __init__(self, config: dict = None):
        """Initialize your plugin."""
        self.config = config or {}
    
    def execute(self, **kwargs):
        """Main plugin functionality."""
        # Your implementation here
        pass
```

### 2. Register via Entry Points

Add your plugin to `pyproject.toml`:

```toml
[project.entry-points."agent_labs.tools"]
my_custom_tool = "my_package.tools:MyCustomTool"

[project.entry-points."agent_labs.models"]
my_custom_model = "my_package.models:MyCustomModel"

[project.entry-points."agent_labs.engines"]
my_custom_engine = "my_package.engines:MyCustomEngine"

[project.entry-points."agent_labs.exporters"]
my_custom_exporter = "my_package.exporters:MyCustomExporter"
```

### 3. Install Your Package

```bash
# Development mode
pip install -e .

# Or regular installation
pip install my-plugin-package
```

### 4. Verify Registration

```python
from agent_labs.registry import Registry, EntryPointLoader

class ToolRegistry(Registry):
    plugin_type = "agent_labs.tools"

registry = ToolRegistry()
loader = EntryPointLoader(group="agent_labs.tools")
count = loader.load_plugins(registry)

print(f"Loaded {count} tool plugins")
print(f"Available tools: {registry.list_plugins()}")
```

## Plugin Types

### Tool Plugins

Tools extend agent capabilities with new actions:

```python
from agent_labs.tools import Tool, ToolContract, ToolResult

class WeatherTool(Tool):
    """Get weather information for a location."""
    
    __version__ = "1.0.0"
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="weather",
            description="Get current weather for a location",
        )
        self.api_key = api_key
    
    async def execute(self, location: str, **kwargs) -> ToolResult:
        """Execute the weather lookup."""
        # Implementation
        return ToolResult(
            output={"temperature": 72, "conditions": "sunny"},
            status="success"
        )
```

Register in `pyproject.toml`:
```toml
[project.entry-points."agent_labs.tools"]
weather = "my_package.tools:WeatherTool"
```

### Model Provider Plugins

Model providers add support for new LLM backends:

```python
from agent_labs.llm_providers import Provider, LLMResponse

class CustomProvider(Provider):
    """Custom LLM provider."""
    
    __version__ = "1.0.0"
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from model."""
        # Implementation
        return LLMResponse(
            text="Generated response",
            tokens_used=100,
            model="custom-model"
        )
    
    async def stream(self, prompt: str, **kwargs):
        """Stream response tokens."""
        # Implementation
        pass
```

Register in `pyproject.toml`:
```toml
[project.entry-points."agent_labs.models"]
custom_provider = "my_package.providers:CustomProvider"
```

## Using the Registry API

### Manual Registration

Register plugins directly without entry points:

```python
from agent_labs.registry import Registry, PluginMetadata

class ToolRegistry(Registry):
    plugin_type = "agent_labs.tools"

registry = ToolRegistry()

# Register with lazy loading (default)
registry.register("my_tool", MyToolClass, lazy=True)

# Register with immediate loading
registry.register("eager_tool", EagerToolClass, lazy=False, config={"key": "value"})

# Register with custom metadata
metadata = PluginMetadata(
    name="custom_tool",
    version="2.0.0",
    description="A custom tool",
    author="Me"
)
registry.register("custom_tool", CustomToolClass, metadata=metadata)
```

### Loading Plugins

```python
# Load a specific plugin
tool = registry.get("my_tool")  # Loads on first access

# Get plugin without loading
info = registry.get("my_tool", load=False)

# Check if loaded
is_loaded = registry.is_loaded("my_tool")

# List all plugins
all_plugins = registry.list_plugins()

# List only loaded plugins
loaded_plugins = registry.list_plugins(loaded_only=True)
```

### Plugin Lifecycle

```python
# Reload a plugin (useful for development)
registry.reload("my_tool")

# Unregister a plugin
registry.unregister("my_tool")

# Clear all plugins
registry.clear()
```

### Getting Metadata

```python
# Get metadata without loading plugin
metadata = registry.get_metadata("my_tool")

print(f"Name: {metadata.name}")
print(f"Version: {metadata.version}")
print(f"Description: {metadata.description}")
print(f"Dependencies: {metadata.dependencies}")
print(f"Tags: {metadata.tags}")
```

## Automatic Discovery

Use the convenience function for automatic plugin discovery:

```python
from agent_labs.registry import Registry, discover_plugins

class ToolRegistry(Registry):
    plugin_type = "agent_labs.tools"

registry = ToolRegistry()

# Discover and register all plugins from entry points
count = discover_plugins(registry, lazy=True)
print(f"Discovered {count} plugins")

# Now use the plugins
tool = registry.get("my_custom_tool")
```

## Creating a Custom Registry

Extend the base Registry class for your specific use case:

```python
from agent_labs.registry import Registry, discover_plugins

class ModelRegistry(Registry):
    """Registry for LLM model providers."""
    
    plugin_type = "agent_labs.models"
    
    def __init__(self):
        super().__init__()
        # Auto-discover plugins on init
        discover_plugins(self, lazy=True)
    
    def get_provider(self, name: str, **init_kwargs):
        """Get a model provider with initialization."""
        plugin_class = self.get(name, load=False)
        if plugin_class:
            return plugin_class(**init_kwargs)
        return None

# Usage
registry = ModelRegistry()
provider = registry.get_provider("openai", api_key="sk-...")
```

## Best Practices

### 1. Plugin Metadata

Always include metadata in your plugin classes:

```python
class MyPlugin:
    __version__ = "1.0.0"          # Semantic version
    __author__ = "Your Name"       # Author info
    __dependencies__ = [           # Runtime dependencies
        "httpx>=0.24.0",
        "pydantic>=2.0"
    ]
    __tags__ = ["utility", "data"] # Categorization
```

### 2. Initialization Parameters

Make initialization flexible with sensible defaults:

```python
def __init__(self, api_key: str = None, timeout: int = 30):
    self.api_key = api_key or os.getenv("MY_PLUGIN_API_KEY")
    self.timeout = timeout
```

### 3. Error Handling

Handle errors gracefully:

```python
def execute(self, **kwargs):
    try:
        # Your logic
        pass
    except Exception as e:
        logger.error(f"Plugin execution failed: {e}")
        raise
```

### 4. Documentation

Document your plugin thoroughly:

```python
class MyPlugin:
    """
    Plugin for doing amazing things.
    
    This plugin provides functionality for X, Y, and Z.
    
    Args:
        api_key: API key for authentication
        timeout: Request timeout in seconds
    
    Example:
        >>> plugin = MyPlugin(api_key="key")
        >>> result = plugin.execute(param="value")
    """
```

### 5. Testing

Test your plugins independently:

```python
import pytest

def test_my_plugin():
    plugin = MyPlugin(api_key="test_key")
    result = plugin.execute(param="test")
    assert result is not None
```

### 6. Lazy Loading

Use lazy loading for expensive plugins:

```python
# Heavy dependencies only imported when needed
class HeavyPlugin:
    def __init__(self):
        # Import here, not at module level
        import heavy_library
        self.lib = heavy_library
```

## Example: Complete Plugin Package

Here's a complete example of a plugin package structure:

```
my-agent-plugin/
├── pyproject.toml
├── README.md
├── src/
│   └── my_agent_plugin/
│       ├── __init__.py
│       ├── tools.py
│       └── models.py
└── tests/
    ├── test_tools.py
    └── test_models.py
```

**pyproject.toml:**
```toml
[project]
name = "my-agent-plugin"
version = "1.0.0"
dependencies = ["ai_agents>=0.1.0", "httpx>=0.24.0"]

[project.entry-points."agent_labs.tools"]
my_tool = "my_agent_plugin.tools:MyTool"

[project.entry-points."agent_labs.models"]
my_model = "my_agent_plugin.models:MyModel"
```

**src/my_agent_plugin/tools.py:**
```python
class MyTool:
    """My custom tool."""
    
    __version__ = "1.0.0"
    __author__ = "Me"
    __dependencies__ = ["httpx>=0.24.0"]
    __tags__ = ["custom", "example"]
    
    def execute(self, **kwargs):
        return {"result": "success"}
```

## Troubleshooting

### Plugin Not Discovered

1. Verify entry point group name matches registry's `plugin_type`
2. Check that package is installed: `pip list | grep my-plugin`
3. Verify entry point registration: `python -m pip show my-plugin`

### Import Errors

1. Ensure all dependencies are installed
2. Check Python path and virtual environment
3. Verify module and class names in entry point

### Plugin Not Loading

1. Check logs for error messages
2. Try manual registration to isolate issue
3. Verify plugin class is importable: `python -c "from my_package import MyPlugin"`

## Advanced Topics

### Custom Loaders

Create custom loaders for non-entry-point plugin sources:

```python
from agent_labs.registry import PluginLoader

class FileSystemLoader(PluginLoader):
    """Load plugins from file system."""
    
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
    
    def load_plugins(self, registry: Registry) -> int:
        # Scan directory and load plugins
        # Return count of loaded plugins
        pass
```

### Plugin Dependencies

Handle plugin dependencies:

```python
class PluginManager:
    def __init__(self, registry: Registry):
        self.registry = registry
    
    def load_with_dependencies(self, name: str):
        metadata = self.registry.get_metadata(name)
        
        # Load dependencies first
        for dep in metadata.dependencies:
            if dep not in self.registry:
                self.install_dependency(dep)
        
        # Then load plugin
        return self.registry.get(name)
```

## Related Documentation

- [Configuration Guide](configuration.md) - Configuration system documentation
- [Registry Module](../src/agent_labs/registry/README.md) - Plugin registry API reference
- [Tool System](../src/agent_labs/tools/) - Tool development
- [LLM Providers](../src/agent_labs/llm_providers/) - Provider development
