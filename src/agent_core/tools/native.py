"""Native tool provider for built-in tools."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .builtin import CalculatorTool, FileReadTool, WebSearchTool
from .contract import ToolContract, ToolResult
from .exceptions import ToolNotFound
from .provider import Tool, ToolProvider


class NativeToolProvider(ToolProvider):
    """Provide access to in-process built-in tools."""

    def __init__(self, tools: Mapping[str, Tool] | None = None) -> None:
        if tools is None:
            tools = {
                "calculator": CalculatorTool(),
                "web_search": WebSearchTool(),
                "file_read": FileReadTool(),
            }
        self._tools = dict(tools)

    async def list_tools(self) -> Sequence[ToolContract]:
        return [tool.contract for tool in self._tools.values()]

    async def execute(self, tool_name: str, args: Mapping[str, Any]) -> ToolResult:
        tool = self._tools.get(tool_name)
        if tool is None:
            raise ToolNotFound(f"Tool '{tool_name}' not found in native provider.")
        return await tool.execute(**dict(args))

    def get_tool(self, tool_name: str) -> Tool | None:
        return self._tools.get(tool_name)


__all__ = ["NativeToolProvider"]
