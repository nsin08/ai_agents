"""MCP (Model Context Protocol) errors.

This module intentionally keeps a small error taxonomy so MCP adapters can map
remote-tool failures onto local tool execution statuses.
"""


class McpError(RuntimeError):
    """Base error for MCP client and tool invocation failures."""


class McpConnectionError(McpError):
    """Raised when the MCP server cannot be reached."""


class McpTimeoutError(McpError):
    """Raised when an MCP tool call exceeds the timeout."""


class McpToolNotFoundError(McpError):
    """Raised when a requested tool does not exist on the MCP server."""


class McpInvalidArgumentsError(McpError):
    """Raised when tool arguments fail schema validation on the server side."""

