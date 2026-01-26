"""Tests for deterministic config validation."""

from __future__ import annotations

import pytest

from agent_core.config.models import AgentCoreConfig, AppConfig, ModelSpec, ModelsConfig, ToolsConfig


def test_deterministic_config_allows_fixture(deterministic_config: AgentCoreConfig) -> None:
    deterministic_config.validate_deterministic()


def test_deterministic_requires_fixture_provider() -> None:
    config = AgentCoreConfig(
        app=AppConfig(name="test", environment="local"),
        mode="deterministic",
        models=ModelsConfig(
            roles={"actor": ModelSpec(provider="mock", model="deterministic")}
        ),
        tools=ToolsConfig(providers={}),
    )

    with pytest.raises(ValueError, match="fixture tool provider"):
        config.validate_deterministic()


def test_deterministic_requires_fixture_path() -> None:
    config = AgentCoreConfig(
        app=AppConfig(name="test", environment="local"),
        mode="deterministic",
        models=ModelsConfig(
            roles={"actor": ModelSpec(provider="mock", model="deterministic")}
        ),
        tools=ToolsConfig(providers={"fixture": {}}),
    )

    with pytest.raises(ValueError, match="fixture tool provider path"):
        config.validate_deterministic()


def test_deterministic_requires_mock_models() -> None:
    config = AgentCoreConfig(
        app=AppConfig(name="test", environment="local"),
        mode="deterministic",
        models=ModelsConfig(
            roles={"actor": ModelSpec(provider="openai", model="gpt-4o")}
        ),
        tools=ToolsConfig(providers={"fixture": {"path": "tests/fixtures/tool_fixtures.json"}}),
    )

    with pytest.raises(ValueError, match="Deterministic mode requires mock providers"):
        config.validate_deterministic()
