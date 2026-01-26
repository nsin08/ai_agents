"""Built-in implementations for agent_core registries."""

from __future__ import annotations

from .engine import LocalEngine
from .providers import MockProvider, OllamaProvider, OpenAIProvider
from .tools import FixtureToolProviderAdapter, McpToolProvider, NativeToolProvider


class MemoryVectorStore:
    """Stub vector store placeholder."""


class StdoutExporter:
    """Stub exporter placeholder."""


class FileExporter:
    """Stub exporter placeholder."""


class MemoryExporter:
    """Stub exporter placeholder."""


__all__ = [
    "FileExporter",
    "FixtureToolProviderAdapter",
    "LocalEngine",
    "McpToolProvider",
    "MemoryExporter",
    "MemoryVectorStore",
    "MockProvider",
    "NativeToolProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "StdoutExporter",
]
