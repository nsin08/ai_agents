"""
Tests for plugin registry system.

Tests:
1. Registry base class functionality
2. Plugin registration (eager and lazy)
3. Plugin retrieval and loading
4. Metadata tracking
5. Lifecycle management (load, reload, unload)
"""

import pytest

from src.agent_labs.registry import PluginInfo, PluginMetadata, Registry


# Test plugin classes
class MockPlugin:
    """Mock plugin for testing."""

    __version__ = "1.0.0"
    __author__ = "Test Author"
    __dependencies__ = ["dep1", "dep2"]
    __tags__ = ["test", "mock"]

    def __init__(self, value: str = "default"):
        self.value = value
        self.initialized = True

    def get_value(self) -> str:
        return self.value


class AnotherMockPlugin:
    """Another mock plugin."""

    def __init__(self):
        self.name = "another"


class FailingPlugin:
    """Plugin that fails on initialization."""

    def __init__(self):
        raise RuntimeError("Initialization failed")


# Test registry implementation
class TestPluginRegistry(Registry):
    """Test registry for mock plugins."""

    plugin_type = "test.plugins"


class TestPluginMetadata:
    """Tests for PluginMetadata dataclass."""

    def test_metadata_creation_minimal(self):
        """Test creating metadata with minimal fields."""
        metadata = PluginMetadata(name="test_plugin")

        assert metadata.name == "test_plugin"
        assert metadata.version == "0.0.0"
        assert metadata.description == ""
        assert metadata.author == ""
        assert metadata.entry_point is None
        assert metadata.dependencies == []
        assert metadata.tags == []

    def test_metadata_creation_full(self):
        """Test creating metadata with all fields."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.2.3",
            description="Test plugin",
            author="Test Author",
            entry_point="test.plugin:TestPlugin",
            dependencies=["dep1", "dep2"],
            tags=["test", "example"],
        )

        assert metadata.name == "test_plugin"
        assert metadata.version == "1.2.3"
        assert metadata.description == "Test plugin"
        assert metadata.author == "Test Author"
        assert metadata.entry_point == "test.plugin:TestPlugin"
        assert metadata.dependencies == ["dep1", "dep2"]
        assert metadata.tags == ["test", "example"]


class TestPluginInfo:
    """Tests for PluginInfo dataclass."""

    def test_plugin_info_creation(self):
        """Test creating plugin info."""
        metadata = PluginMetadata(name="test")
        info = PluginInfo(
            metadata=metadata,
            plugin_class=MockPlugin,
            instance=None,
            is_loaded=False,
        )

        assert info.metadata == metadata
        assert info.plugin_class == MockPlugin
        assert info.instance is None
        assert info.is_loaded is False
        assert info.loader is None


class TestRegistry:
    """Tests for Registry base class."""

    def test_registry_initialization(self):
        """Test registry starts empty."""
        registry = TestPluginRegistry()

        assert len(registry) == 0
        assert registry.list_plugins() == []

    def test_register_plugin_eager(self):
        """Test registering a plugin with immediate loading."""
        registry = TestPluginRegistry()

        registry.register("test", MockPlugin, lazy=False, value="custom")

        assert len(registry) == 1
        assert "test" in registry
        assert registry.is_loaded("test")

        plugin = registry.get("test")
        assert plugin is not None
        assert plugin.value == "custom"
        assert plugin.initialized is True

    def test_register_plugin_lazy(self):
        """Test registering a plugin with lazy loading."""
        registry = TestPluginRegistry()

        registry.register("test", MockPlugin, lazy=True, value="lazy_value")

        assert len(registry) == 1
        assert "test" in registry
        assert not registry.is_loaded("test")

        # Plugin should not be loaded yet
        plugin = registry.get("test", load=False)
        assert plugin is None

        # Now load it
        plugin = registry.get("test", load=True)
        assert plugin is not None
        assert plugin.value == "lazy_value"
        assert registry.is_loaded("test")

    def test_register_plugin_with_custom_metadata(self):
        """Test registering with custom metadata."""
        metadata = PluginMetadata(
            name="custom",
            version="2.0.0",
            description="Custom plugin",
            author="Custom Author",
        )

        registry = TestPluginRegistry()
        registry.register("custom", MockPlugin, metadata=metadata, lazy=False)

        retrieved_metadata = registry.get_metadata("custom")
        assert retrieved_metadata is not None
        assert retrieved_metadata.name == "custom"
        assert retrieved_metadata.version == "2.0.0"
        assert retrieved_metadata.description == "Custom plugin"
        assert retrieved_metadata.author == "Custom Author"

    def test_register_plugin_auto_metadata(self):
        """Test automatic metadata extraction from plugin class."""
        registry = TestPluginRegistry()
        registry.register("auto", MockPlugin, lazy=False)

        metadata = registry.get_metadata("auto")
        assert metadata is not None
        assert metadata.name == "auto"
        assert "Mock plugin for testing" in metadata.description

    def test_register_duplicate_plugin_fails(self):
        """Test registering same plugin name twice fails."""
        registry = TestPluginRegistry()
        registry.register("test", MockPlugin, lazy=False)

        with pytest.raises(ValueError, match="already registered"):
            registry.register("test", AnotherMockPlugin, lazy=False)

    def test_register_failing_plugin_eager(self):
        """Test registering plugin that fails on init (eager mode)."""
        registry = TestPluginRegistry()

        with pytest.raises(RuntimeError, match="Initialization failed"):
            registry.register("failing", FailingPlugin, lazy=False)

    def test_register_failing_plugin_lazy(self):
        """Test registering plugin that fails on init (lazy mode)."""
        registry = TestPluginRegistry()

        # Registration succeeds (lazy)
        registry.register("failing", FailingPlugin, lazy=True)
        assert "failing" in registry

        # But loading fails
        with pytest.raises(RuntimeError, match="Initialization failed"):
            registry.get("failing", load=True)

    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = TestPluginRegistry()
        registry.register("test", MockPlugin, lazy=False)

        assert "test" in registry
        assert registry.unregister("test") is True
        assert "test" not in registry
        assert len(registry) == 0

    def test_unregister_nonexistent_plugin(self):
        """Test unregistering plugin that doesn't exist."""
        registry = TestPluginRegistry()

        assert registry.unregister("nonexistent") is False

    def test_get_nonexistent_plugin(self):
        """Test getting plugin that doesn't exist."""
        registry = TestPluginRegistry()

        assert registry.get("nonexistent") is None
        assert registry.get_metadata("nonexistent") is None

    def test_list_plugins_all(self):
        """Test listing all registered plugins."""
        registry = TestPluginRegistry()
        registry.register("plugin1", MockPlugin, lazy=True)
        registry.register("plugin2", AnotherMockPlugin, lazy=False)

        plugins = registry.list_plugins()
        assert len(plugins) == 2
        assert "plugin1" in plugins
        assert "plugin2" in plugins

    def test_list_plugins_loaded_only(self):
        """Test listing only loaded plugins."""
        registry = TestPluginRegistry()
        registry.register("plugin1", MockPlugin, lazy=True)
        registry.register("plugin2", AnotherMockPlugin, lazy=False)

        loaded_plugins = registry.list_plugins(loaded_only=True)
        assert len(loaded_plugins) == 1
        assert "plugin2" in loaded_plugins

    def test_reload_plugin(self):
        """Test reloading a plugin."""
        registry = TestPluginRegistry()
        registry.register("test", MockPlugin, lazy=False, value="original")

        plugin1 = registry.get("test")
        assert plugin1.value == "original"

        # Modify the instance
        plugin1.value = "modified"
        assert plugin1.value == "modified"

        # Reload should create new instance
        assert registry.reload("test") is True
        plugin2 = registry.get("test")

        # New instance should have original value
        assert plugin2.value == "original"
        assert plugin2 is not plugin1

    def test_reload_nonexistent_plugin(self):
        """Test reloading plugin that doesn't exist."""
        registry = TestPluginRegistry()

        assert registry.reload("nonexistent") is False

    def test_clear_registry(self):
        """Test clearing all plugins."""
        registry = TestPluginRegistry()
        registry.register("plugin1", MockPlugin, lazy=False)
        registry.register("plugin2", AnotherMockPlugin, lazy=False)

        assert len(registry) == 2

        registry.clear()

        assert len(registry) == 0
        assert registry.list_plugins() == []

    def test_registry_repr(self):
        """Test string representation of registry."""
        registry = TestPluginRegistry()
        registry.register("plugin1", MockPlugin, lazy=True)
        registry.register("plugin2", AnotherMockPlugin, lazy=False)

        repr_str = repr(registry)

        assert "TestPluginRegistry" in repr_str
        assert "plugins=2" in repr_str
        assert "loaded=1" in repr_str
        assert "test.plugins" in repr_str

    def test_multiple_plugin_types(self):
        """Test multiple plugins with different configurations."""
        registry = TestPluginRegistry()

        registry.register("eager1", MockPlugin, lazy=False, value="eager1")
        registry.register("lazy1", MockPlugin, lazy=True, value="lazy1")
        registry.register("eager2", AnotherMockPlugin, lazy=False)

        assert len(registry) == 3
        assert registry.is_loaded("eager1")
        assert not registry.is_loaded("lazy1")
        assert registry.is_loaded("eager2")

        # Load lazy plugin
        plugin = registry.get("lazy1")
        assert plugin.value == "lazy1"
        assert registry.is_loaded("lazy1")


class TestRegistrySubclassing:
    """Tests for creating custom registry subclasses."""

    def test_custom_registry_with_plugin_type(self):
        """Test creating a custom registry with plugin type."""

        class ToolRegistry(Registry):
            plugin_type = "agent_labs.tools"

        registry = ToolRegistry()

        assert registry.plugin_type == "agent_labs.tools"
        assert len(registry) == 0

    def test_registry_without_plugin_type(self):
        """Test registry can work without plugin_type."""

        class GenericRegistry(Registry):
            pass

        registry = GenericRegistry()

        # Should still work for manual registration
        registry.register("test", MockPlugin, lazy=False)
        assert len(registry) == 1
