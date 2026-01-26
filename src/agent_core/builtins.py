"""Built-in implementations for agent_core registries."""

from __future__ import annotations

from .providers import FixtureToolProvider, MockProvider, OllamaProvider, OpenAIProvider


class LocalEngine:
    """Stub execution engine placeholder."""


class NativeToolProvider:
    """Stub tool provider placeholder."""


class McpToolProvider:
    """Stub MCP tool provider placeholder."""


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
    "FixtureToolProvider",
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
