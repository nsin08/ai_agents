"""Tests for agent_core registries."""

from __future__ import annotations

import pytest

from agent_core.exceptions import ImplementationNotFoundError
from agent_core.registry import Registry, get_global_registry


class Example:
    pass


def test_registry_register_and_get() -> None:
    registry = Registry("example")
    registry.register("example", Example)

    assert registry.get("example") is Example


def test_registry_uses_plugin_loader_on_miss() -> None:
    def loader(key: str) -> None:
        if key == "dynamic":
            registry.register("dynamic", Example)

    registry = Registry("example", plugin_loader=loader)

    assert registry.get("dynamic") is Example


def test_registry_missing_key_raises() -> None:
    registry = Registry("example")

    with pytest.raises(ImplementationNotFoundError, match="missing"):
        registry.get("missing")


def test_builtin_registrations_present() -> None:
    registry = get_global_registry()

    assert "local" in registry.engines
    assert "mock" in registry.model_providers
    assert "ollama" in registry.model_providers
    assert "openai" in registry.model_providers
    assert "native" in registry.tool_providers
    assert "mcp" in registry.tool_providers
    assert "fixture" in registry.tool_providers
    assert "memory" in registry.vectorstores
