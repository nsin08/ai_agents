"""
Integration tests for plugin system with real entry points.

These tests demonstrate the complete plugin lifecycle including:
- Entry point discovery
- Plugin registration
- Lazy and eager loading
- Plugin execution
"""

import pytest

from src.agent_labs.registry import EntryPointLoader, Registry, discover_plugins


class TestPluginSystemIntegration:
    """Integration tests for complete plugin system."""

    def test_empty_entry_points(self):
        """Test that system handles no plugins gracefully."""

        class EmptyRegistry(Registry):
            plugin_type = "agent_labs.nonexistent"

        registry = EmptyRegistry()
        loader = EntryPointLoader(group="agent_labs.nonexistent")

        count = loader.load_plugins(registry)

        assert count == 0
        assert len(registry) == 0
        assert registry.list_plugins() == []

    def test_discover_plugins_convenience(self):
        """Test discover_plugins convenience function."""

        class TestRegistry(Registry):
            plugin_type = "agent_labs.tools"

        registry = TestRegistry()

        # This should work even if no plugins are registered
        count = discover_plugins(registry, lazy=True)

        assert count >= 0
        assert isinstance(count, int)

    def test_manual_registration_workflow(self):
        """Test complete manual registration workflow."""

        # Define a test plugin
        class CustomPlugin:
            __version__ = "1.0.0"
            __author__ = "Test"

            def __init__(self, config=None):
                self.config = config or {}
                self.executed = False

            def execute(self):
                self.executed = True
                return "success"

        # Create registry
        class PluginRegistry(Registry):
            plugin_type = "test.plugins"

        registry = PluginRegistry()

        # Register plugin
        registry.register("custom", CustomPlugin, lazy=True, config={"key": "value"})

        # Verify not loaded yet
        assert not registry.is_loaded("custom")

        # Load and use
        plugin = registry.get("custom")
        assert plugin.config["key"] == "value"
        assert plugin.executed is False

        result = plugin.execute()
        assert result == "success"
        assert plugin.executed is True

        # Verify now loaded
        assert registry.is_loaded("custom")

    def test_multiple_registries(self):
        """Test that different registries are independent."""

        class ToolRegistry(Registry):
            plugin_type = "agent_labs.tools"

        class ModelRegistry(Registry):
            plugin_type = "agent_labs.models"

        class DummyPlugin:
            pass

        tool_registry = ToolRegistry()
        model_registry = ModelRegistry()

        tool_registry.register("plugin1", DummyPlugin, lazy=False)
        model_registry.register("plugin2", DummyPlugin, lazy=False)

        assert "plugin1" in tool_registry
        assert "plugin1" not in model_registry

        assert "plugin2" in model_registry
        assert "plugin2" not in tool_registry

    def test_plugin_registry_persistence(self):
        """Test that registry maintains state across operations."""

        class Plugin1:
            value = 1

        class Plugin2:
            value = 2

        class TestRegistry(Registry):
            plugin_type = "test.persistence"

        registry = TestRegistry()

        # Register multiple plugins
        registry.register("p1", Plugin1, lazy=False)
        registry.register("p2", Plugin2, lazy=True)

        # Get first plugin
        p1 = registry.get("p1")
        assert p1.value == 1

        # State should persist
        assert "p1" in registry
        assert "p2" in registry

        # Get second plugin (triggers lazy load)
        p2 = registry.get("p2")
        assert p2.value == 2

        # Both should now be loaded
        assert registry.is_loaded("p1")
        assert registry.is_loaded("p2")

        # State still persists
        assert len(registry) == 2

        # Can still get them
        assert registry.get("p1") is p1  # Same instance
        assert registry.get("p2") is p2  # Same instance


class TestPluginLifecycleIntegration:
    """Integration tests for plugin lifecycle management."""

    def test_full_lifecycle(self):
        """Test complete plugin lifecycle."""

        class CounterPlugin:
            instance_count = 0

            def __init__(self):
                CounterPlugin.instance_count += 1
                self.id = CounterPlugin.instance_count

        class TestRegistry(Registry):
            plugin_type = "test.lifecycle"

        registry = TestRegistry()

        # Register
        registry.register("counter", CounterPlugin, lazy=True)
        assert CounterPlugin.instance_count == 0  # Not instantiated yet

        # Load
        plugin1 = registry.get("counter")
        assert plugin1.id == 1
        assert CounterPlugin.instance_count == 1

        # Get again (should be same instance)
        plugin2 = registry.get("counter")
        assert plugin2 is plugin1
        assert CounterPlugin.instance_count == 1  # No new instance

        # Reload (should create new instance)
        registry.reload("counter")
        plugin3 = registry.get("counter")
        assert plugin3 is not plugin1
        assert plugin3.id == 2
        assert CounterPlugin.instance_count == 2

        # Unregister
        registry.unregister("counter")
        assert "counter" not in registry
        assert registry.get("counter") is None

    def test_error_recovery(self):
        """Test recovery from plugin errors."""

        class FailingPlugin:
            def __init__(self, fail: bool = True):
                if fail:
                    raise RuntimeError("Initialization failed")
                self.status = "ok"

        class TestRegistry(Registry):
            plugin_type = "test.errors"

        registry = TestRegistry()

        # Register with lazy loading (should succeed)
        registry.register("failing", FailingPlugin, lazy=True, fail=True)
        assert "failing" in registry

        # Try to load (should fail)
        with pytest.raises(RuntimeError, match="Initialization failed"):
            registry.get("failing")

        # Plugin is still registered but not loaded
        assert "failing" in registry
        assert not registry.is_loaded("failing")

        # Can unregister and try again with working version
        registry.unregister("failing")
        registry.register("working", FailingPlugin, lazy=False, fail=False)

        plugin = registry.get("working")
        assert plugin.status == "ok"


class TestPluginRegistryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_registry_operations(self):
        """Test operations on empty registry."""

        class TestRegistry(Registry):
            plugin_type = "test.empty"

        registry = TestRegistry()

        assert len(registry) == 0
        assert registry.list_plugins() == []
        assert registry.list_plugins(loaded_only=True) == []
        assert registry.get("nonexistent") is None
        assert registry.get_metadata("nonexistent") is None
        assert not registry.is_loaded("nonexistent")
        assert not registry.unregister("nonexistent")
        assert not registry.reload("nonexistent")

        # Should not raise
        registry.clear()

    def test_plugin_with_no_metadata(self):
        """Test plugin class with no metadata attributes."""

        class BarePlugin:
            pass

        class TestRegistry(Registry):
            plugin_type = "test.bare"

        registry = TestRegistry()
        registry.register("bare", BarePlugin, lazy=False)

        metadata = registry.get_metadata("bare")
        assert metadata.name == "bare"
        assert metadata.version == "0.0.0"
        assert metadata.dependencies == []
        assert metadata.tags == []

    def test_registry_with_no_plugin_type(self):
        """Test registry without plugin_type still works for manual registration."""

        class NoTypeRegistry(Registry):
            pass

        class DummyPlugin:
            pass

        registry = NoTypeRegistry()

        # Manual registration should still work
        registry.register("dummy", DummyPlugin, lazy=False)

        assert "dummy" in registry
        assert len(registry) == 1

        # But discovery should fail
        with pytest.raises(ValueError, match="must define plugin_type"):
            discover_plugins(registry)
