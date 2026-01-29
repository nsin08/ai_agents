"""Tests for agent_core plugin loader."""

from __future__ import annotations

import importlib

import pytest

from agent_core.exceptions import PluginDependencyError, PluginNotFoundError
from agent_core.plugin_loader import load_plugin
from agent_core.registry import (
    AgentCoreRegistry,
    ExecutionEngineRegistry,
    ExporterRegistry,
    ModelProviderRegistry,
    ToolProviderRegistry,
    VectorStoreRegistry,
)
import agent_core.plugin_loader as plugin_loader


class FakeEntryPoint:
    def __init__(self, name: str, loader):
        self.name = name
        self._loader = loader

    def load(self):
        return self._loader()


def _make_registry() -> AgentCoreRegistry:
    return AgentCoreRegistry(
        engines=ExecutionEngineRegistry("engine"),
        model_providers=ModelProviderRegistry("model_provider"),
        tool_providers=ToolProviderRegistry("tool_provider"),
        vectorstores=VectorStoreRegistry("vector_store"),
        exporters=ExporterRegistry("exporter"),
    )


def test_load_plugin_registers_entry_point(monkeypatch) -> None:
    registry = _make_registry()

    def loader():
        return importlib.import_module("tests.fixtures.mock_plugin")

    fake_eps = [FakeEntryPoint("mock_plugin", loader)]
    monkeypatch.setattr(plugin_loader, "_iter_entry_points", lambda: fake_eps)
    plugin_loader._loaded_plugins.clear()

    load_plugin("mock_plugin", registry=registry)

    assert "mock_plugin_engine" in registry.engines


def test_load_plugin_missing_entry_point(monkeypatch) -> None:
    registry = _make_registry()

    monkeypatch.setattr(plugin_loader, "_iter_entry_points", lambda: [])
    plugin_loader._loaded_plugins.clear()

    with pytest.raises(PluginNotFoundError, match="missing"):
        load_plugin("missing", registry=registry)


def test_load_plugin_missing_dependency(monkeypatch) -> None:
    registry = _make_registry()

    def loader():
        raise ModuleNotFoundError("no module named optional_dep")

    fake_eps = [FakeEntryPoint("missing_dep", loader)]
    monkeypatch.setattr(plugin_loader, "_iter_entry_points", lambda: fake_eps)
    plugin_loader._loaded_plugins.clear()

    with pytest.raises(PluginDependencyError, match=r"Install ai_agents\[missing_dep\]"):
        load_plugin("missing_dep", registry=registry)
