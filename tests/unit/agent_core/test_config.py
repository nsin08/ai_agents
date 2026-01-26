"""Tests for agent_core configuration loading."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agent_core.config import AgentCoreConfig, load_config


def test_default_config_constructs():
    config = AgentCoreConfig()
    assert config.app.name == "agent_core_app"
    assert config.engine.key == "local"
    assert config.mode == "real"


def test_load_config_from_json(tmp_path: Path):
    config_path = tmp_path / "config.json"
    data = {
        "app": {"name": "test_app", "environment": "local"},
        "mode": "deterministic",
        "models": {"roles": {"actor": {"provider": "mock", "model": "det"}}},
        "tools": {"providers": {"fixture": {"path": "tests/fixtures/tool_fixtures.json"}}},
    }
    config_path.write_text(json.dumps(data), encoding="utf-8")

    config = load_config(path=str(config_path))
    assert config.app.name == "test_app"
    assert config.mode == "deterministic"
    assert config.models.roles["actor"].provider == "mock"


def test_env_override(monkeypatch):
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__PROVIDER", "mock")
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__MODEL", "det")
    monkeypatch.setenv("AGENT_CORE_MODE", "deterministic")
    monkeypatch.setenv("AGENT_CORE_TOOLS__PROVIDERS__FIXTURE__PATH", "tests/fixtures/tool_fixtures.json")

    config = load_config(load_dotenv_file=False)
    assert config.mode == "deterministic"
    assert config.models.roles["actor"].provider == "mock"
    assert config.models.roles["actor"].model == "det"


def test_deterministic_validation_requires_mock(monkeypatch):
    monkeypatch.setenv("AGENT_CORE_MODE", "deterministic")
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__PROVIDER", "ollama")
    monkeypatch.setenv("AGENT_CORE_MODELS__ROLES__ACTOR__MODEL", "llama")

    with pytest.raises(ValueError, match="Deterministic mode requires mock"):
        load_config(load_dotenv_file=False)

