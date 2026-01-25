"""
Plugin Registry System - Generic registry with entry point discovery.

This module provides:
1. Registry - Generic base class for plugin registration
2. PluginLoader - Entry point discovery and lazy loading
3. Plugin metadata and lifecycle management

Example:
    >>> from agent_labs.registry import Registry, PluginLoader
    >>>
    >>> # Define a registry for a specific plugin type
    >>> class ToolPluginRegistry(Registry):
    ...     plugin_type = "agent_labs.tools"
    ...
    >>> registry = ToolPluginRegistry()
    >>> registry.discover_plugins()  # Auto-discover from entry points
    >>> tool = registry.get("my_tool")  # Lazy load on first access
"""

from .base import PluginInfo, PluginMetadata, Registry
from .loader import EntryPointLoader, PluginLoader, discover_plugins

__all__ = [
    # Core classes
    "Registry",
    "PluginMetadata",
    "PluginInfo",
    # Loaders
    "PluginLoader",
    "EntryPointLoader",
    # Functions
    "discover_plugins",
]
