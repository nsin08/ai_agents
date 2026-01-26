"""Registries for agent_core pluggable components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Iterator, Optional

from . import builtins
from .exceptions import ImplementationNotFoundError
from .plugin_loader import load_plugin

class Registry:
    """Registry mapping stable keys to constructors."""

    def __init__(self, name: str, plugin_loader: Optional[Callable[[str], None]] = None) -> None:
        self._name = name
        self._implementations: Dict[str, Callable[..., Any]] = {}
        self._plugin_loader = plugin_loader

    def register(self, key: str, constructor: Callable[..., Any]) -> None:
        if not isinstance(key, str) or not key:
            raise ValueError("Registry keys must be non-empty strings.")
        if not callable(constructor):
            raise ValueError("Registry constructor must be callable.")
        self._implementations[key] = constructor

    def unregister(self, key: str) -> bool:
        return self._implementations.pop(key, None) is not None

    def get(self, key: str) -> Callable[..., Any]:
        if key not in self._implementations and self._plugin_loader:
            self._plugin_loader(key)
        if key not in self._implementations:
            available = ", ".join(sorted(self._implementations))
            raise ImplementationNotFoundError(
                f"No implementation for '{key}' in {self._name} registry. "
                f"Available: {available}"
            )
        return self._implementations[key]

    def keys(self) -> Iterable[str]:
        return self._implementations.keys()

    def __contains__(self, key: object) -> bool:
        return key in self._implementations

    def __len__(self) -> int:
        return len(self._implementations)

    def __iter__(self) -> Iterator[str]:
        return iter(self._implementations)


class ExecutionEngineRegistry(Registry):
    """Registry for execution engine implementations."""


class ModelProviderRegistry(Registry):
    """Registry for model provider implementations."""


class ToolProviderRegistry(Registry):
    """Registry for tool provider implementations."""


class VectorStoreRegistry(Registry):
    """Registry for vector store backends."""


class ExporterRegistry(Registry):
    """Registry for observability exporters."""


@dataclass(frozen=True)
class AgentCoreRegistry:
    """Container for all agent_core registries."""

    engines: ExecutionEngineRegistry
    model_providers: ModelProviderRegistry
    tool_providers: ToolProviderRegistry
    vectorstores: VectorStoreRegistry
    exporters: ExporterRegistry


_ENGINE_REGISTRY = ExecutionEngineRegistry("engine", plugin_loader=load_plugin)
_MODEL_PROVIDER_REGISTRY = ModelProviderRegistry("model_provider", plugin_loader=load_plugin)
_TOOL_PROVIDER_REGISTRY = ToolProviderRegistry("tool_provider", plugin_loader=load_plugin)
_VECTORSTORE_REGISTRY = VectorStoreRegistry("vector_store", plugin_loader=load_plugin)
_EXPORTER_REGISTRY = ExporterRegistry("exporter", plugin_loader=load_plugin)

_AGENT_CORE_REGISTRY = AgentCoreRegistry(
    engines=_ENGINE_REGISTRY,
    model_providers=_MODEL_PROVIDER_REGISTRY,
    tool_providers=_TOOL_PROVIDER_REGISTRY,
    vectorstores=_VECTORSTORE_REGISTRY,
    exporters=_EXPORTER_REGISTRY,
)


def get_global_registry() -> AgentCoreRegistry:
    return _AGENT_CORE_REGISTRY


# Built-in registrations (eager, import time)
_ENGINE_REGISTRY.register("local", builtins.LocalEngine)

_MODEL_PROVIDER_REGISTRY.register("mock", builtins.MockProvider)
_MODEL_PROVIDER_REGISTRY.register("ollama", builtins.OllamaProvider)
_MODEL_PROVIDER_REGISTRY.register("openai", builtins.OpenAIProvider)

_TOOL_PROVIDER_REGISTRY.register("native", builtins.NativeToolProvider)
_TOOL_PROVIDER_REGISTRY.register("mcp", builtins.McpToolProvider)
_TOOL_PROVIDER_REGISTRY.register("fixture", builtins.FixtureToolProviderAdapter)

_VECTORSTORE_REGISTRY.register("memory", builtins.MemoryVectorStore)

_EXPORTER_REGISTRY.register("stdout", builtins.StdoutExporter)
_EXPORTER_REGISTRY.register("file", builtins.FileExporter)
_EXPORTER_REGISTRY.register("memory", builtins.MemoryExporter)


__all__ = [
    "AgentCoreRegistry",
    "ExecutionEngineRegistry",
    "ModelProviderRegistry",
    "ToolProviderRegistry",
    "VectorStoreRegistry",
    "ExporterRegistry",
    "Registry",
    "get_global_registry",
]
