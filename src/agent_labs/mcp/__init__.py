"""MCP (Model Context Protocol) adapters.

This package provides a small interface layer for MCP-style tool servers and
an adapter to run MCP tools through the existing `agent_labs.tools.ToolRegistry`.
"""

from .client import McpClient
from .errors import (
    McpError,
    McpConnectionError,
    McpTimeoutError,
    McpToolNotFoundError,
    McpInvalidArgumentsError,
)
from .types import McpTool, McpToolCallResult
from .tool_adapter import McpToolAdapter

__all__ = [
    "McpClient",
    "McpTool",
    "McpToolCallResult",
    "McpToolAdapter",
    "McpError",
    "McpConnectionError",
    "McpTimeoutError",
    "McpToolNotFoundError",
    "McpInvalidArgumentsError",
]

