"""Error types for agent_core registries and plugins."""

from __future__ import annotations


class RegistryError(RuntimeError):
    """Base error for registry operations."""


class ImplementationNotFoundError(RegistryError):
    """Raised when a registry key cannot be resolved."""


class PluginLoadError(RegistryError):
    """Raised when a plugin fails to load or register."""


class PluginNotFoundError(PluginLoadError):
    """Raised when no entry point matches the requested plugin key."""


class PluginDependencyError(PluginLoadError):
    """Raised when a plugin dependency is missing."""
