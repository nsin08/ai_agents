"""Fake MCP server/client for offline labs.

This intentionally does not implement the full MCP spec. It provides the same
two primitives needed for teaching:
- list_tools()
- call_tool(name, arguments)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.agent_labs.mcp import (
    McpInvalidArgumentsError,
    McpTool,
    McpToolCallResult,
    McpToolNotFoundError,
)


@dataclass
class FakeMcpConfig:
    timeout_s: Optional[float] = None


class FakeMcpClient:
    def __init__(self, config: Optional[FakeMcpConfig] = None) -> None:
        self.config = config or FakeMcpConfig()
        self.calls: list[dict] = []
        self._tools = [
            McpTool(
                name="echo",
                description="Echo back input text.",
                input_schema={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
                output_schema={"type": "string"},
            ),
            McpTool(
                name="add",
                description="Add two numbers.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"},
                    },
                    "required": ["a", "b"],
                },
                output_schema={"type": "number"},
            ),
        ]

    def list_tools(self) -> List[McpTool]:
        return list(self._tools)

    def call_tool(
        self,
        name: str,
        arguments: Dict[str, object],
        *,
        timeout_s: Optional[float] = None,
    ) -> McpToolCallResult:
        self.calls.append({"name": name, "arguments": dict(arguments), "timeout_s": timeout_s})

        if name == "echo":
            if "text" not in arguments:
                raise McpInvalidArgumentsError("Missing required field: text")
            return McpToolCallResult(content=str(arguments["text"]), metadata={"server": "fake"})

        if name == "add":
            if "a" not in arguments or "b" not in arguments:
                raise McpInvalidArgumentsError("Missing required fields: a, b")
            return McpToolCallResult(
                content=float(arguments["a"]) + float(arguments["b"]),
                metadata={"server": "fake"},
            )

        raise McpToolNotFoundError(f"Tool not found: {name}")

