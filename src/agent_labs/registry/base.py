"""
Generic Registry base class for plugin management.

Provides:
- Plugin registration and retrieval
- Lifecycle management (load, unload, reload)
- Lazy loading support
- Plugin metadata tracking
"""

import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata about a registered plugin."""

    name: str
    """Unique plugin identifier."""

    version: str = "0.0.0"
    """Plugin version (semver format)."""

    description: str = ""
    """Human-readable description."""

    author: str = ""
    """Plugin author/maintainer."""

    entry_point: Optional[str] = None
    """Entry point string if loaded from setuptools."""

    dependencies: List[str] = field(default_factory=list)
    """List of required dependencies."""

    tags: List[str] = field(default_factory=list)
    """Categorization tags."""


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""

    metadata: PluginMetadata
    """Plugin metadata."""

    plugin_class: Optional[Type] = None
    """Plugin class (not instantiated yet if lazy)."""

    instance: Optional[Any] = None
    """Loaded plugin instance (None if not yet loaded)."""

    is_loaded: bool = False
    """Whether plugin has been instantiated."""

    loader: Optional[Callable] = None
    """Lazy loader function (called on first access)."""


class Registry(ABC):
    """
    Generic registry for managing plugins with lazy loading.

    Subclasses should define:
    - plugin_type: str - Unique identifier for entry point group

    Features:
    - Registration of plugins by name
    - Lazy loading (plugins loaded on first access)
    - Plugin lifecycle management
    - Metadata tracking
    - Entry point discovery (via PluginLoader)

    Example:
        >>> class ModelRegistry(Registry):
        ...     plugin_type = "agent_labs.models"
        ...
        >>> registry = ModelRegistry()
        >>> registry.register("my_model", MyModelClass, lazy=True)
        >>> model = registry.get("my_model")  # Loads on first access
    """

    # Subclasses should override this
    plugin_type: Optional[str] = None

    def __init__(self):
        """Initialize empty registry."""
        self._plugins: Dict[str, PluginInfo] = {}
        self._initialized = False

    def register(
        self,
        name: str,
        plugin_class: Type,
        metadata: Optional[PluginMetadata] = None,
        lazy: bool = True,
        **init_kwargs,
    ) -> None:
        """
        Register a plugin.

        Args:
            name: Unique plugin identifier
            plugin_class: Plugin class to register
            metadata: Optional plugin metadata
            lazy: If True, instantiate on first access; if False, instantiate now
            **init_kwargs: Arguments to pass to plugin constructor

        Raises:
            ValueError: If plugin name already registered
        """
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered")

        # Create default metadata if not provided
        if metadata is None:
            metadata = PluginMetadata(
                name=name,
                description=plugin_class.__doc__ or "",
            )

        # Create plugin info
        info = PluginInfo(
            metadata=metadata,
            plugin_class=plugin_class,
            is_loaded=False,
        )

        # Store loader function for both lazy and eager modes (needed for reload)
        def loader():
            return plugin_class(**init_kwargs)

        info.loader = loader

        # If not lazy, instantiate immediately
        if not lazy:
            try:
                info.instance = plugin_class(**init_kwargs)
                info.is_loaded = True
                logger.info(f"Registered and loaded plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to instantiate plugin '{name}': {e}")
                raise
        else:
            logger.info(f"Registered plugin for lazy loading: {name}")

        self._plugins[name] = info

    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            name: Plugin name to unregister

        Returns:
            True if plugin was removed, False if not found
        """
        if name in self._plugins:
            del self._plugins[name]
            logger.info(f"Unregistered plugin: {name}")
            return True
        return False

    def get(self, name: str, load: bool = True) -> Optional[Any]:
        """
        Get a plugin by name, loading it if necessary.

        Args:
            name: Plugin name to retrieve
            load: If True and plugin is lazy, load it now

        Returns:
            Plugin instance if found and loaded, None otherwise
        """
        if name not in self._plugins:
            return None

        info = self._plugins[name]

        # If already loaded, return instance
        if info.is_loaded:
            return info.instance

        # If lazy and load requested, instantiate now
        if load and info.loader is not None:
            try:
                info.instance = info.loader()
                info.is_loaded = True
                logger.info(f"Lazy loaded plugin: {name}")
                return info.instance
            except Exception as e:
                logger.error(f"Failed to lazy load plugin '{name}': {e}")
                raise

        # Not loaded and not loading
        return None

    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """
        Get plugin metadata without loading the plugin.

        Args:
            name: Plugin name

        Returns:
            PluginMetadata if found, None otherwise
        """
        info = self._plugins.get(name)
        return info.metadata if info else None

    def list_plugins(self, loaded_only: bool = False) -> List[str]:
        """
        List all registered plugin names.

        Args:
            loaded_only: If True, only return loaded plugins

        Returns:
            List of plugin names
        """
        if loaded_only:
            return [name for name, info in self._plugins.items() if info.is_loaded]
        return list(self._plugins.keys())

    def is_loaded(self, name: str) -> bool:
        """
        Check if a plugin is loaded.

        Args:
            name: Plugin name

        Returns:
            True if plugin is loaded, False otherwise
        """
        info = self._plugins.get(name)
        return info.is_loaded if info else False

    def reload(self, name: str) -> bool:
        """
        Reload a plugin (unload and load again).

        Args:
            name: Plugin name to reload

        Returns:
            True if reload successful, False if plugin not found
        """
        info = self._plugins.get(name)
        if not info:
            return False

        # If loaded, clear instance
        if info.is_loaded:
            info.instance = None
            info.is_loaded = False

        # Load again if loader available
        if info.loader:
            try:
                info.instance = info.loader()
                info.is_loaded = True
                logger.info(f"Reloaded plugin: {name}")
                return True
            except Exception as e:
                logger.error(f"Failed to reload plugin '{name}': {e}")
                raise

        return False

    def clear(self) -> None:
        """Remove all plugins from registry."""
        self._plugins.clear()
        logger.info("Cleared all plugins from registry")

    def __len__(self) -> int:
        """Get number of registered plugins."""
        return len(self._plugins)

    def __contains__(self, name: str) -> bool:
        """Check if plugin is registered."""
        return name in self._plugins

    def __repr__(self) -> str:
        """String representation of registry."""
        loaded_count = sum(1 for info in self._plugins.values() if info.is_loaded)
        return (
            f"{self.__class__.__name__}("
            f"plugins={len(self._plugins)}, "
            f"loaded={loaded_count}, "
            f"type={self.plugin_type!r})"
        )
