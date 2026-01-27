"""Integration test for secret redaction in tool events."""

from __future__ import annotations

import pytest

from agent_core.config.models import ObservabilityConfig, RedactConfig
from agent_core.tools import ToolExecutor
from agent_core.tools.contract import ExecutionStatus, ToolCall, ToolContract, ToolDataHandling, ToolResult


class SecretToolProvider:
    def __init__(self) -> None:
        self._contract = ToolContract(
            name="secret_tool",
            description="Returns secret output",
            data_handling=ToolDataHandling(secrets=True),
        )

    async def list_tools(self):
        return [self._contract]

    async def execute(self, tool_name, arguments):
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"token": "super-secret"})


@pytest.mark.asyncio
@pytest.mark.integration
async def test_secret_redaction_in_events() -> None:
    events: list[dict] = []
    executor = ToolExecutor(
        providers=[SecretToolProvider()],
        allowlist=["secret_tool"],
        observability=ObservabilityConfig(redact=RedactConfig(pii=True, secrets=True)),
        emit_event=events.append,
    )

    result = await executor.execute(
        ToolCall(tool_name="secret_tool", arguments={"token": "super-secret"}, run_id="run-1")
    )

    assert result.status == ExecutionStatus.SUCCESS
    finished = [event for event in events if event.get("event_type") == "tool.call.finished"]
    assert finished
    attrs = finished[0]["attrs"]
    assert attrs["arguments"] == "<redacted>"
    assert attrs["output"] == "<redacted>"
