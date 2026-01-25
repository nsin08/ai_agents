"""
Tests for plugin loader and entry point discovery.

Tests:
1. Entry point discovery
2. Plugin loading from entry points
3. Metadata extraction
4. Error handling
5. Integration with Registry
"""

from importlib.metadata import EntryPoint
from unittest.mock import Mock, patch

import pytest

from src.agent_labs.registry import (
    EntryPointLoader,
    PluginLoader,
    Registry,
)
from src.agent_labs.registry.loader import discover_plugins


# Test plugin classes
class ExampleTool:
    """Example tool plugin."""

    __version__ = "1.5.0"
    __author__ = "Tool Developer"
    __dependencies__ = ["httpx", "pydantic"]
    __tags__ = ["utility", "example"]

    def __init__(self):
        self.name = "example_tool"


class ExampleModel:
    """Example model plugin."""

    def __init__(self):
        self.name = "example_model"


class TestPluginRegistry(Registry):
    """Test registry for plugins."""

    plugin_type = "test.plugins"


class TestEntryPointLoader:
    """Tests for EntryPointLoader."""

    def test_loader_initialization(self):
        """Test creating an entry point loader."""
        loader = EntryPointLoader(group="agent_labs.tools", lazy=True)

        assert loader.group == "agent_labs.tools"
        assert loader.lazy is True

    def test_loader_repr(self):
        """Test string representation."""
        loader = EntryPointLoader(group="test.group", lazy=False)

        repr_str = repr(loader)
        assert "EntryPointLoader" in repr_str
        assert "test.group" in repr_str
        assert "lazy=False" in repr_str

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_discover_entry_points_empty(self, mock_entry_points):
        """Test discovering entry points when none exist."""
        mock_entry_points.return_value = []

        loader = EntryPointLoader(group="test.plugins")
        eps = loader.discover_entry_points()

        assert eps == []
        mock_entry_points.assert_called_once_with(group="test.plugins")

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_discover_entry_points_found(self, mock_entry_points):
        """Test discovering entry points when they exist."""
        # Create mock entry points
        ep1 = Mock(spec=EntryPoint)
        ep1.name = "tool1"
        ep1.value = "test.tools:Tool1"

        ep2 = Mock(spec=EntryPoint)
        ep2.name = "tool2"
        ep2.value = "test.tools:Tool2"

        mock_entry_points.return_value = [ep1, ep2]

        loader = EntryPointLoader(group="test.plugins")
        eps = loader.discover_entry_points()

        assert len(eps) == 2
        assert eps[0].name == "tool1"
        assert eps[1].name == "tool2"

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_discover_entry_points_python39_fallback(self, mock_entry_points):
        """Test Python 3.9 fallback when entry_points returns dict."""
        # Simulate Python 3.9 behavior (TypeError on group kwarg)
        mock_entry_points.side_effect = [
            TypeError("unexpected keyword argument"),
            {"test.plugins": [Mock(name="ep1"), Mock(name="ep2")]},
        ]

        loader = EntryPointLoader(group="test.plugins")
        eps = loader.discover_entry_points()

        assert len(eps) == 2

    def test_load_entry_point_success(self):
        """Test successfully loading an entry point."""
        ep = Mock(spec=EntryPoint)
        ep.name = "example_tool"
        ep.value = "test.tools:ExampleTool"
        ep.load.return_value = ExampleTool

        loader = EntryPointLoader(group="test.plugins")
        plugin_class = loader.load_entry_point(ep)

        assert plugin_class == ExampleTool
        ep.load.assert_called_once()

    def test_load_entry_point_import_error(self):
        """Test handling import error when loading entry point."""
        ep = Mock(spec=EntryPoint)
        ep.name = "broken_tool"
        ep.value = "test.tools:BrokenTool"
        ep.load.side_effect = ImportError("Module not found")

        loader = EntryPointLoader(group="test.plugins")
        plugin_class = loader.load_entry_point(ep)

        assert plugin_class is None

    def test_load_entry_point_general_error(self):
        """Test handling general error when loading entry point."""
        ep = Mock(spec=EntryPoint)
        ep.name = "error_tool"
        ep.value = "test.tools:ErrorTool"
        ep.load.side_effect = RuntimeError("Something went wrong")

        loader = EntryPointLoader(group="test.plugins")
        plugin_class = loader.load_entry_point(ep)

        assert plugin_class is None

    def test_extract_metadata_full(self):
        """Test extracting full metadata from plugin class."""
        ep = Mock(spec=EntryPoint)
        ep.name = "example_tool"
        ep.value = "test.tools:ExampleTool"

        loader = EntryPointLoader(group="test.plugins")
        metadata = loader.extract_metadata(ep, ExampleTool)

        assert metadata.name == "example_tool"
        assert metadata.version == "1.5.0"
        assert "Example tool plugin" in metadata.description
        assert metadata.author == "Tool Developer"
        assert metadata.entry_point == "test.tools:ExampleTool"
        assert metadata.dependencies == ["httpx", "pydantic"]
        assert metadata.tags == ["utility", "example"]

    def test_extract_metadata_minimal(self):
        """Test extracting metadata when plugin has minimal info."""
        ep = Mock(spec=EntryPoint)
        ep.name = "minimal_tool"
        ep.value = "test.tools:MinimalTool"

        class MinimalTool:
            pass

        loader = EntryPointLoader(group="test.plugins")
        metadata = loader.extract_metadata(ep, MinimalTool)

        assert metadata.name == "minimal_tool"
        assert metadata.version == "0.0.0"
        assert metadata.description == ""
        assert metadata.author == ""
        assert metadata.entry_point == "test.tools:MinimalTool"
        assert metadata.dependencies == []
        assert metadata.tags == []

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_load_plugins_integration(self, mock_entry_points):
        """Test loading plugins from entry points into registry."""
        # Create mock entry point
        ep = Mock(spec=EntryPoint)
        ep.name = "example_tool"
        ep.value = "test.tools:ExampleTool"
        ep.load.return_value = ExampleTool

        mock_entry_points.return_value = [ep]

        # Create registry and loader
        registry = TestPluginRegistry()
        loader = EntryPointLoader(group="test.plugins", lazy=True)

        # Load plugins
        count = loader.load_plugins(registry)

        assert count == 1
        assert "example_tool" in registry
        assert not registry.is_loaded("example_tool")  # Lazy loaded

        # Verify metadata
        metadata = registry.get_metadata("example_tool")
        assert metadata.name == "example_tool"
        assert metadata.version == "1.5.0"

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_load_plugins_eager_mode(self, mock_entry_points):
        """Test loading plugins in eager mode."""
        ep = Mock(spec=EntryPoint)
        ep.name = "example_tool"
        ep.value = "test.tools:ExampleTool"
        ep.load.return_value = ExampleTool

        mock_entry_points.return_value = [ep]

        registry = TestPluginRegistry()
        loader = EntryPointLoader(group="test.plugins", lazy=False)

        count = loader.load_plugins(registry)

        assert count == 1
        assert registry.is_loaded("example_tool")  # Eager loaded

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_load_plugins_no_entry_points(self, mock_entry_points):
        """Test loading when no entry points found."""
        mock_entry_points.return_value = []

        registry = TestPluginRegistry()
        loader = EntryPointLoader(group="test.plugins")

        count = loader.load_plugins(registry)

        assert count == 0
        assert len(registry) == 0

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_load_plugins_some_fail(self, mock_entry_points):
        """Test loading when some entry points fail."""
        ep1 = Mock(spec=EntryPoint)
        ep1.name = "good_tool"
        ep1.value = "test.tools:GoodTool"
        ep1.load.return_value = ExampleTool

        ep2 = Mock(spec=EntryPoint)
        ep2.name = "bad_tool"
        ep2.value = "test.tools:BadTool"
        ep2.load.side_effect = ImportError("Not found")

        ep3 = Mock(spec=EntryPoint)
        ep3.name = "another_good_tool"
        ep3.value = "test.tools:AnotherGoodTool"
        ep3.load.return_value = ExampleModel

        mock_entry_points.return_value = [ep1, ep2, ep3]

        registry = TestPluginRegistry()
        loader = EntryPointLoader(group="test.plugins")

        count = loader.load_plugins(registry)

        # Only 2 should load successfully
        assert count == 2
        assert "good_tool" in registry
        assert "bad_tool" not in registry
        assert "another_good_tool" in registry

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_load_plugins_duplicate_names(self, mock_entry_points):
        """Test handling duplicate plugin names."""
        ep1 = Mock(spec=EntryPoint)
        ep1.name = "duplicate"
        ep1.value = "test.tools:Tool1"
        ep1.load.return_value = ExampleTool

        ep2 = Mock(spec=EntryPoint)
        ep2.name = "duplicate"
        ep2.value = "test.tools:Tool2"
        ep2.load.return_value = ExampleModel

        mock_entry_points.return_value = [ep1, ep2]

        registry = TestPluginRegistry()
        loader = EntryPointLoader(group="test.plugins")

        count = loader.load_plugins(registry)

        # Only first should load
        assert count == 1
        assert "duplicate" in registry


class TestDiscoverPluginsFunction:
    """Tests for discover_plugins convenience function."""

    @patch("src.agent_labs.registry.loader.entry_points")
    def test_discover_plugins_success(self, mock_entry_points):
        """Test discover_plugins convenience function."""
        ep = Mock(spec=EntryPoint)
        ep.name = "test_plugin"
        ep.value = "test:Plugin"
        ep.load.return_value = ExampleTool

        mock_entry_points.return_value = [ep]

        registry = TestPluginRegistry()
        count = discover_plugins(registry, lazy=True)

        assert count == 1
        assert "test_plugin" in registry

    def test_discover_plugins_no_plugin_type(self):
        """Test discover_plugins fails without plugin_type."""

        class NoTypeRegistry(Registry):
            pass

        registry = NoTypeRegistry()

        with pytest.raises(ValueError, match="must define plugin_type"):
            discover_plugins(registry)


class TestPluginLoaderInterface:
    """Tests for PluginLoader base interface."""

    def test_plugin_loader_is_abstract(self):
        """Test PluginLoader requires subclassing."""
        loader = PluginLoader()
        registry = TestPluginRegistry()

        with pytest.raises(NotImplementedError):
            loader.load_plugins(registry)
