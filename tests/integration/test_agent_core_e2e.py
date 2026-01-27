"""Integration tests for AgentCore public API."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_core.api import AgentCore
from agent_core.engine import RunRequest, RunStatus


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_core_from_file_run_e2e() -> None:
    config_path = Path("tests/fixtures/agent_core_test_config.json")
    core = AgentCore.from_file(str(config_path))

    result = await core.run(RunRequest(input="hello"))

    assert result.status == RunStatus.SUCCESS
    assert result.output_text
