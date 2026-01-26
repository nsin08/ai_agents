"""Tool provider interfaces for agent_core."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .contract import ToolContract, ToolResult


@runtime_checkable
class Tool(Protocol):
    contract: ToolContract

    async def execute(self, **kwargs: Any) -> ToolResult:
        ...


@runtime_checkable
class ToolProvider(Protocol):
    async def list_tools(self) -> Sequence[ToolContract]:
        ...

    async def execute(self, tool_name: str, args: Mapping[str, Any]) -> ToolResult:
        ...


__all__ = ["Tool", "ToolProvider"]
