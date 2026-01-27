"""Integration test for tool timeouts."""

from __future__ import annotations

import asyncio

import pytest

from agent_core.tools import ToolExecutor
from agent_core.tools.contract import ExecutionStatus, ToolCall, ToolContract, ToolResult


class SlowToolProvider:
    def __init__(self) -> None:
        self._contract = ToolContract(name="slow_tool", description="Sleeps")

    async def list_tools(self):
        return [self._contract]

    async def execute(self, tool_name, arguments):
        await asyncio.sleep(0.05)
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"ok": True})


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tool_timeout_enforced() -> None:
    executor = ToolExecutor(
        providers=[SlowToolProvider()],
        allowlist=["slow_tool"],
    )

    result = await executor.execute(
        ToolCall(tool_name="slow_tool", arguments={}, timeout_ms=1)
    )

    assert result.status == ExecutionStatus.TIMEOUT
