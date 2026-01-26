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

    def build_role_map(self, roles: Mapping[str, Any]) -> dict[str, Any]:
        providers: dict[str, Any] = {}
        for role, spec in roles.items():
            spec_dict: Mapping[str, Any] | None = None
            if isinstance(spec, Mapping):
                spec_dict = spec
            elif hasattr(spec, "model_dump"):
                spec_dict = spec.model_dump()
            if spec_dict is None:
                raise ValueError(f"Model spec for role '{role}' must be a mapping.")
            provider_key = str(spec_dict.get("provider", "")).strip()
            if not provider_key:
                raise ValueError(f"Model spec for role '{role}' missing provider key.")
            config = dict(spec_dict)
            config.pop("provider", None)
            providers[role] = self.build(provider_key, config)
        return providers


class ToolProviderFactory:
    """Build tool providers from registry + config."""

    def __init__(self, registry: ToolProviderRegistry) -> None:
        self._registry = registry

    def build(self, key: str, config: Mapping[str, Any] | None = None) -> Any:
        return _build_from_registry(self._registry, key, config)


__all__ = ["EngineFactory", "ModelFactory", "ToolProviderFactory"]
