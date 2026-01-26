"""Shared pytest fixtures for agent_core."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_core.config.models import AgentCoreConfig, AppConfig, ModelSpec, ModelsConfig, ToolsConfig
from agent_core.providers import FixtureToolProvider, MockProvider


@pytest.fixture
def mock_responses() -> list[str]:
    path = Path("tests/fixtures/mock_responses.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


@pytest.fixture
def mock_provider(mock_responses: list[str]) -> MockProvider:
    return MockProvider(responses=mock_responses, seed=123)


@pytest.fixture
def fixture_tool_provider() -> FixtureToolProvider:
    return FixtureToolProvider("tests/fixtures/tool_fixtures.json")


@pytest.fixture
def deterministic_config() -> AgentCoreConfig:
    return AgentCoreConfig(
        app=AppConfig(name="test", environment="local"),
        mode="deterministic",
        models=ModelsConfig(
            roles={
                "actor": ModelSpec(provider="mock", model="deterministic"),
            }
        ),
        tools=ToolsConfig(providers={"fixture": {"path": "tests/fixtures/tool_fixtures.json"}}),
    )
