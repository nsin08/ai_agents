"""
Example: Integrating Plugin Registry with existing ToolRegistry.

This example demonstrates how to extend the existing ToolRegistry
with plugin capabilities for dynamic tool discovery.
"""

from agent_labs.registry import Registry, discover_plugins
from agent_labs.tools import ToolRegistry as ExistingToolRegistry, Tool


class PluginableToolRegistry(Registry):
    """
    Enhanced tool registry with plugin support.

    Extends the base Registry to support both:
    1. Entry point discovery (new plugin system)
    2. Traditional tool registration (existing system)

    Example:
        >>> registry = PluginableToolRegistry()
        >>> # Auto-discover plugins from entry points
        >>> count = registry.discover_plugins()
        >>> print(f"Discovered {count} tool plugins")
        >>>
        >>> # Traditional registration still works
        >>> from agent_labs.tools.builtin import Calculator
        >>> registry.register_tool(Calculator())
    """

    plugin_type = "agent_labs.tools"

    def __init__(self, auto_discover: bool = True):
        """
        Initialize tool registry.

        Args:
            auto_discover: If True, automatically discover plugins on init
        """
        super().__init__()
        self._traditional_tools = ExistingToolRegistry()

        if auto_discover:
            self.discover_plugins()

    def discover_plugins(self) -> int:
        """
        Discover and register tools from entry points.

        Returns:
            Number of plugins discovered
        """
        return discover_plugins(self, lazy=True)

    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool instance using traditional method.

        Args:
            tool: Tool instance to register
        """
        self._traditional_tools.register(tool)

    def get_tool(self, name: str, load: bool = True):
        """
        Get a tool by name from either plugin or traditional registry.

        Args:
            name: Tool name
            load: If True, lazy load plugin if needed

        Returns:
            Tool instance or None
        """
        # Try plugin registry first
        tool = self.get(name, load=load)
        if tool is not None:
            return tool

        # Fall back to traditional registry
        return self._traditional_tools.get(name)

    def list_all_tools(self) -> list[str]:
        """
        List all available tools (plugins + traditional).

        Returns:
            List of tool names
        """
        plugin_tools = self.list_plugins()
        traditional_tools = self._traditional_tools.list_tools()

        # Combine and deduplicate
        return list(set(plugin_tools + traditional_tools))

    async def execute_tool(self, name: str, **kwargs):
        """
        Execute a tool by name.

        Args:
            name: Tool name to execute
            **kwargs: Arguments to pass to tool

        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)

        if tool is None:
            raise ValueError(f"Tool '{name}' not found")

        # Check if it's from plugin registry (class) or traditional (instance)
        if isinstance(tool, type):
            # Plugin: instantiate then execute
            tool_instance = tool()
            return await tool_instance.execute(**kwargs)
        else:
            # Traditional: already an instance
            return await self._traditional_tools.execute(name, **kwargs)


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Plugin Registry Usage ===")

    # Create registry with auto-discovery
    registry = PluginableToolRegistry(auto_discover=True)

    # List discovered tools
    tools = registry.list_all_tools()
    print(f"Available tools: {tools}")

    # Get metadata for a plugin
    for tool_name in registry.list_plugins():
        metadata = registry.get_metadata(tool_name)
        print(f"\nTool: {metadata.name}")
        print(f"  Version: {metadata.version}")
        print(f"  Description: {metadata.description}")
        print(f"  Author: {metadata.author}")


def example_custom_registry():
    """Example of creating a specialized registry."""
    print("\n=== Custom Model Registry ===")

    class ModelRegistry(Registry):
        """Registry for LLM model providers."""

        plugin_type = "agent_labs.models"

        def get_provider(self, name: str, **config):
            """Get a provider instance with configuration."""
            provider_class = self.get(name, load=False)
            if provider_class:
                # Instantiate with config
                return provider_class(**config)
            return None

    # Create registry
    registry = ModelRegistry()

    # Discover providers
    count = discover_plugins(registry, lazy=True)
    print(f"Discovered {count} model providers")

    # List available providers
    providers = registry.list_plugins()
    print(f"Available providers: {providers}")


def example_manual_registration():
    """Example of manual plugin registration."""
    print("\n=== Manual Registration ===")

    class MyCustomTool:
        """A custom tool for demonstration."""

        __version__ = "1.0.0"
        __author__ = "Example Developer"

        async def execute(self, query: str):
            return f"Processed: {query}"

    registry = PluginableToolRegistry(auto_discover=False)

    # Manual registration
    registry.register("my_tool", MyCustomTool, lazy=True)

    print(f"Registered tools: {registry.list_plugins()}")

    # Check metadata
    metadata = registry.get_metadata("my_tool")
    print(f"Tool: {metadata.name} v{metadata.version}")
    print(f"Author: {metadata.author}")


def example_lifecycle_management():
    """Example of plugin lifecycle management."""
    print("\n=== Lifecycle Management ===")

    class ToolV1:
        version = "1.0"

        async def execute(self):
            return "v1 result"

    class ToolV2:
        version = "2.0"

        async def execute(self):
            return "v2 result"

    registry = PluginableToolRegistry(auto_discover=False)

    # Register v1
    registry.register("demo_tool", ToolV1, lazy=False)
    tool = registry.get("demo_tool")
    print(f"Initial: {tool.version}")

    # Reload with v2
    registry.unregister("demo_tool")
    registry.register("demo_tool", ToolV2, lazy=False)
    tool = registry.get("demo_tool")
    print(f"After reload: {tool.version}")


if __name__ == "__main__":
    print("Plugin Registry Examples\n")

    try:
        example_basic_usage()
    except Exception as e:
        print(f"Note: No plugins registered yet: {e}")

    try:
        example_custom_registry()
    except Exception as e:
        print(f"Note: {e}")

    example_manual_registration()
    example_lifecycle_management()

    print("\n✅ Examples completed!")
