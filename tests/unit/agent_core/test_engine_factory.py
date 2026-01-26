"""Tests for EngineFactory build_with_config."""

from __future__ import annotations

import pytest

from agent_core.config.models import AgentCoreConfig, EngineConfig, ToolsConfig
from agent_core.factories import EngineFactory, ToolExecutorFactory
from agent_core.registry import get_global_registry


@pytest.mark.asyncio
async def test_engine_factory_wires_tool_executor() -> None:
    registry = get_global_registry()
    config = AgentCoreConfig(
        engine=EngineConfig(key="local"),
        tools=ToolsConfig(allowlist=["calculator"]),
    )

    engine_factory = EngineFactory(registry.engines)
    tool_factory = ToolExecutorFactory(registry.tool_providers)

    engine = engine_factory.build_with_config(config, tool_executor_factory=tool_factory)

    assert hasattr(engine, "tool_executor")
    assert engine.tool_executor is not None
