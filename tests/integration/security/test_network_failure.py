"""Integration test for tool provider network failure handling."""

from __future__ import annotations

import pytest

from agent_core.tools import ToolExecutor
from agent_core.tools.contract import ToolCall, ToolContract
from agent_core.tools.exceptions import ToolProviderError


class FailingToolProvider:
    def __init__(self) -> None:
        self._contract = ToolContract(name="failing_tool", description="Fails")

    async def list_tools(self):
        return [self._contract]

    async def execute(self, tool_name, arguments):
        raise ToolProviderError("network down")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_network_failure_handled() -> None:
    executor = ToolExecutor(
        providers=[FailingToolProvider()],
        allowlist=["failing_tool"],
    )

    result = await executor.execute(ToolCall(tool_name="failing_tool", arguments={}))

    assert result.error is not None
    assert result.error.type == "ToolProviderError"
