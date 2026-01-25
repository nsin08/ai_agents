"""
Plugin loader with entry point discovery.

Provides:
- Entry point discovery using setuptools
- Plugin loading from entry points
- Error handling for missing dependencies
"""

import logging
from importlib.metadata import EntryPoint, entry_points
from typing import List, Optional, Type

from .base import PluginMetadata, Registry

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Base plugin loader interface.

    Subclasses implement different loading strategies
    (entry points, file system, remote, etc.)
    """

    def load_plugins(self, registry: Registry) -> int:
        """
        Load plugins into a registry.

        Args:
            registry: Target registry to load plugins into

        Returns:
            Number of plugins successfully loaded
        """
        raise NotImplementedError("Subclasses must implement load_plugins()")


class EntryPointLoader(PluginLoader):
    """
    Load plugins from setuptools entry points.

    Entry points should be defined in pyproject.toml:

        [project.entry-points."agent_labs.tools"]
        my_tool = "my_package.tools:MyTool"

        [project.entry-points."agent_labs.models"]
        my_model = "my_package.models:MyModel"

    Example:
        >>> from agent_labs.registry import Registry, EntryPointLoader
        >>>
        >>> class ToolRegistry(Registry):
        ...     plugin_type = "agent_labs.tools"
        ...
        >>> registry = ToolRegistry()
        >>> loader = EntryPointLoader(group="agent_labs.tools")
        >>> count = loader.load_plugins(registry)
        >>> print(f"Loaded {count} tool plugins")
    """

    def __init__(self, group: str, lazy: bool = True):
        """
        Initialize entry point loader.

        Args:
            group: Entry point group name (e.g., "agent_labs.tools")
            lazy: If True, register plugins for lazy loading
        """
        self.group = group
        self.lazy = lazy

    def discover_entry_points(self) -> List[EntryPoint]:
        """
        Discover all entry points in the specified group.

        Returns:
            List of EntryPoint objects
        """
        try:
            # Python 3.10+ API
            eps = entry_points(group=self.group)
            return list(eps)
        except TypeError:
            # Python 3.9 fallback (entry_points returns dict)
            eps_dict = entry_points()
            return eps_dict.get(self.group, [])

    def load_entry_point(self, ep: EntryPoint) -> Optional[Type]:
        """
        Load a single entry point.

        Args:
            ep: EntryPoint to load

        Returns:
            Loaded plugin class, or None if loading failed
        """
        try:
            plugin_class = ep.load()
            logger.info(f"Loaded entry point '{ep.name}' from {ep.value}")
            return plugin_class
        except ImportError as e:
            logger.warning(f"Failed to import entry point '{ep.name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading entry point '{ep.name}': {e}")
            return None

    def extract_metadata(self, ep: EntryPoint, plugin_class: Type) -> PluginMetadata:
        """
        Extract metadata from entry point and plugin class.

        Args:
            ep: EntryPoint object
            plugin_class: Loaded plugin class

        Returns:
            PluginMetadata instance
        """
        # Get version from class if available
        version = getattr(plugin_class, "__version__", "0.0.0")

        # Get description from docstring
        description = plugin_class.__doc__ or ""
        if description:
            # Take first line of docstring
            description = description.strip().split("\n")[0]

        # Get author if available
        author = getattr(plugin_class, "__author__", "")

        # Get dependencies if available
        dependencies = getattr(plugin_class, "__dependencies__", [])

        # Get tags if available
        tags = getattr(plugin_class, "__tags__", [])

        return PluginMetadata(
            name=ep.name,
            version=version,
            description=description,
            author=author,
            entry_point=ep.value,
            dependencies=dependencies,
            tags=tags,
        )

    def load_plugins(self, registry: Registry) -> int:
        """
        Load all plugins from entry points into registry.

        Args:
            registry: Target registry

        Returns:
            Number of plugins successfully loaded
        """
        entry_points_list = self.discover_entry_points()

        if not entry_points_list:
            logger.info(f"No entry points found for group '{self.group}'")
            return 0

        loaded_count = 0

        for ep in entry_points_list:
            plugin_class = self.load_entry_point(ep)

            if plugin_class is None:
                continue

            # Extract metadata
            metadata = self.extract_metadata(ep, plugin_class)

            # Register in registry
            try:
                registry.register(
                    name=ep.name,
                    plugin_class=plugin_class,
                    metadata=metadata,
                    lazy=self.lazy,
                )
                loaded_count += 1
            except ValueError as e:
                logger.warning(f"Plugin '{ep.name}' already registered: {e}")
            except Exception as e:
                logger.error(f"Failed to register plugin '{ep.name}': {e}")

        logger.info(f"Loaded {loaded_count}/{len(entry_points_list)} plugins from entry points")
        return loaded_count

    def __repr__(self) -> str:
        """String representation."""
        return f"EntryPointLoader(group={self.group!r}, lazy={self.lazy})"


def discover_plugins(registry: Registry, lazy: bool = True) -> int:
    """
    Convenience function to discover and load plugins for a registry.

    Args:
        registry: Target registry (must have plugin_type defined)
        lazy: If True, register plugins for lazy loading

    Returns:
        Number of plugins loaded

    Raises:
        ValueError: If registry.plugin_type is not set

    Example:
        >>> class ToolRegistry(Registry):
        ...     plugin_type = "agent_labs.tools"
        ...
        >>> registry = ToolRegistry()
        >>> count = discover_plugins(registry)
        >>> print(f"Found {count} tools")
    """
    if not registry.plugin_type:
        raise ValueError(
            f"Registry {registry.__class__.__name__} must define plugin_type "
            "for entry point discovery"
        )

    loader = EntryPointLoader(group=registry.plugin_type, lazy=lazy)
    return loader.load_plugins(registry)
