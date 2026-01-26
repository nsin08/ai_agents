"""Tests for ToolExecutorFactory wiring."""

from __future__ import annotations

import pytest

from agent_core.config.models import AgentCoreConfig, ToolsConfig
from agent_core.factories import ToolExecutorFactory
from agent_core.registry import get_global_registry
from agent_core.tools import ExecutionStatus, ToolCall


@pytest.mark.asyncio
async def test_factory_builds_with_native_provider() -> None:
    registry = get_global_registry()
    config = AgentCoreConfig(
        tools=ToolsConfig(allowlist=["calculator"]),
    )

    factory = ToolExecutorFactory(registry.tool_providers)
    executor = factory.build(config)

    result = await executor.execute(
        ToolCall(tool_name="calculator", arguments={"operation": "add", "a": 1, "b": 2})
    )

    assert result.status == ExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_factory_builds_with_fixture_provider() -> None:
    registry = get_global_registry()
    config = AgentCoreConfig(
        tools=ToolsConfig(
            allowlist=["calculator"],
            providers={"fixture": {"path": "tests/fixtures/tool_fixtures.json"}},
        ),
    )

    factory = ToolExecutorFactory(registry.tool_providers)
    executor = factory.build(config)

    result = await executor.execute(ToolCall(tool_name="calculator", arguments={"a": 2, "b": 2}))

    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == {"value": 4}
