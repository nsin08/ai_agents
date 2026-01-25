"""MCP client protocol.

This is a minimal, offline-testable abstraction. Labs can provide a fake
implementation; production implementations can be added later.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from .types import McpTool, McpToolCallResult


class McpClient(Protocol):
    """Minimal MCP client interface for tool discovery and invocation."""

    def list_tools(self) -> List[McpTool]:
        """Return all tools available on the MCP server."""

    def call_tool(
        self,
        name: str,
        arguments: Dict[str, object],
        *,
        timeout_s: Optional[float] = None,
    ) -> McpToolCallResult:
        """Invoke a tool by name with structured arguments."""

