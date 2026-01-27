"""Performance benchmarks for agent_core."""

from __future__ import annotations

import asyncio
import os
import time

import pytest

from agent_core.api import AgentCore
from agent_core.config.models import AgentCoreConfig, EngineConfig, ModelSpec, ModelsConfig
from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse
from agent_core.providers.openai import OpenAIProvider
from agent_core.tools import ToolExecutor
from agent_core.tools.contract import ToolCall
from agent_core.tools.native import NativeToolProvider


class QuickModel:
    async def generate(self, messages, role):
        last = messages[-1]["content"] if messages else ""
        return ModelResponse(text=f"ok:{last}", role=role)


@pytest.mark.asyncio
@pytest.mark.performance
async def test_mock_run_under_five_seconds() -> None:
    engine = LocalEngine()
    components = EngineComponents(
        models={"planner": QuickModel(), "actor": QuickModel()},
        memory=InMemorySessionStore(),
    )

    start = time.perf_counter()
    result = await engine.execute(RunRequest(input="ping"), components)
    duration = time.perf_counter() - start

    assert result.status == RunStatus.SUCCESS
    assert duration < 5.0


@pytest.mark.asyncio
@pytest.mark.performance
async def test_native_tool_latency_under_100ms() -> None:
    executor = ToolExecutor(
        providers=[NativeToolProvider()],
        allowlist=["calculator"],
    )

    timings = []
    for _ in range(10):
        start = time.perf_counter()
        await executor.execute(
            ToolCall(tool_name="calculator", arguments={"operation": "add", "a": 1, "b": 2})
        )
        timings.append((time.perf_counter() - start) * 1000.0)

    avg_ms = sum(timings) / len(timings)
    assert avg_ms < 100.0


@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_mock_runs_under_30s() -> None:
    engine = LocalEngine()
    model = QuickModel()

    async def run_one(index: int):
        components = EngineComponents(
            models={"planner": model, "actor": model},
            memory=InMemorySessionStore(),
        )
        return await engine.execute(RunRequest(input=f"ping-{index}"), components)

    start = time.perf_counter()
    results = await asyncio.gather(*[run_one(i) for i in range(100)])
    duration = time.perf_counter() - start

    assert all(result.status == RunStatus.SUCCESS for result in results)
    assert duration < 30.0


@pytest.mark.asyncio
@pytest.mark.performance
@pytest.mark.skipif(
    os.getenv("RUN_OPENAI_BENCHMARK", "").strip().lower() not in {"1", "true", "yes"},
    reason="OpenAI benchmark disabled (set RUN_OPENAI_BENCHMARK=true and OPENAI_API_KEY).",
)
async def test_openai_run_under_ten_seconds() -> None:
    model = os.getenv("OPENAI_MODEL", "").strip()
    if not model:
        pytest.skip("OPENAI_MODEL not set")

    provider = OpenAIProvider(model=model)
    engine = LocalEngine()
    components = EngineComponents(
        models={"planner": provider, "actor": provider},
        memory=InMemorySessionStore(),
    )

    start = time.perf_counter()
    result = await engine.execute(RunRequest(input="Hello"), components)
    duration = time.perf_counter() - start

    assert result.status == RunStatus.SUCCESS
    assert duration < 10.0
