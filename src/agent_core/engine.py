"""Local execution engine."""

from __future__ import annotations

from .tools import ToolCall, ToolExecutor, ToolResult


class LocalEngine:
    """Minimal local engine for executing tool calls."""

    def __init__(self, tool_executor: ToolExecutor | None = None) -> None:
        self.tool_executor = tool_executor

    async def execute_tool(self, call: ToolCall) -> ToolResult:
        if self.tool_executor is None:
            raise RuntimeError("ToolExecutor not configured.")
        return await self.tool_executor.execute(call)


__all__ = ["LocalEngine"]
