"""Mock plugin for entry point loading tests."""

from __future__ import annotations


class MockPluginEngine:
    """Mock engine registered by the test plugin."""


def register(registry) -> None:
    registry.engines.register("mock_plugin_engine", MockPluginEngine)
