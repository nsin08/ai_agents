"""Integration test for tool injection/allowlist enforcement."""

from __future__ import annotations

import pytest

from agent_core.tools import ToolExecutor
from agent_core.tools.contract import ToolCall
from agent_core.tools.native import NativeToolProvider


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tool_injection_rejected() -> None:
    executor = ToolExecutor(
        providers=[NativeToolProvider()],
        allowlist=["calculator"],
    )

    result = await executor.execute(ToolCall(tool_name="file_read", arguments={"path": "README.md"}))

    assert result.error is not None
    assert result.error.source == "policy"
