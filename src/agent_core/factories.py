"""Factories for constructing registry-backed components."""

from __future__ import annotations

from typing import Any, Mapping

from .registry import ExecutionEngineRegistry, ModelProviderRegistry, ToolProviderRegistry


def _build_from_registry(
    registry: object,
    key: str,
    config: Mapping[str, Any] | None = None,
) -> Any:
    constructor = registry.get(key)
    if config is None:
        return constructor()
    return constructor(**dict(config))


class EngineFactory:
    """Build execution engines from registry + config."""

    def __init__(self, registry: ExecutionEngineRegistry) -> None:
        self._registry = registry

    def build(self, key: str, config: Mapping[str, Any] | None = None) -> Any:
        return _build_from_registry(self._registry, key, config)


class ModelFactory:
    """Build model providers from registry + config."""

    def __init__(self, registry: ModelProviderRegistry) -> None:
        self._registry = registry

    def build(self, key: str, config: Mapping[str, Any] | None = None) -> Any:
        return _build_from_registry(self._registry, key, config)


class ToolProviderFactory:
    """Build tool providers from registry + config."""

    def __init__(self, registry: ToolProviderRegistry) -> None:
        self._registry = registry

    def build(self, key: str, config: Mapping[str, Any] | None = None) -> Any:
        return _build_from_registry(self._registry, key, config)


__all__ = ["EngineFactory", "ModelFactory", "ToolProviderFactory"]
