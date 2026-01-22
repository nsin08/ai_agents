"""MCP (Model Context Protocol) types.

These types are intentionally small and focused on what the labs need:
- Tool discovery (name, description, input schema)
- Tool invocation (content, metadata, errors)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class McpTool:
    """A discoverable tool published by an MCP tool server."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class McpToolCallResult:
    """Result of invoking an MCP tool."""

    content: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.error is None

