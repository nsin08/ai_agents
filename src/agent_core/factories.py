"""Factories for constructing registry-backed components."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from .registry import ExecutionEngineRegistry, ModelProviderRegistry, ToolProviderRegistry
from .tools import ToolExecutor
from .config.models import AgentCoreConfig


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

    def build_with_config(
        self,
        config: AgentCoreConfig,
        tool_executor_factory: "ToolExecutorFactory | None" = None,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> Any:
        engine_key = config.engine.key
        engine_config = dict(config.engine.config)
        if tool_executor_factory is not None:
            engine_config = dict(engine_config)
            engine_config.setdefault(
                "tool_executor",
                tool_executor_factory.build(config, emit_event=emit_event),
            )
        return _build_from_registry(self._registry, engine_key, engine_config)

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
                # Drop unset values so we don't pass provider-specific unknown kwargs.
                spec_dict = {k: v for k, v in dict(spec).items() if v is not None}
            elif hasattr(spec, "model_dump"):
                # Pydantic models include None fields by default; exclude them so
                # providers only receive explicitly configured arguments.
                spec_dict = spec.model_dump(exclude_none=True)
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


class ToolExecutorFactory:
    """Build ToolExecutor from config and tool provider registry."""

    def __init__(self, registry: ToolProviderRegistry) -> None:
        self._provider_factory = ToolProviderFactory(registry)

    def build(
        self,
        config: AgentCoreConfig,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> ToolExecutor:
        tools_config = config.tools
        providers: list[Any] = []

        if tools_config.providers:
            for key, provider_config in tools_config.providers.items():
                provider_cfg: Mapping[str, Any] | None = None
                if isinstance(provider_config, Mapping):
                    provider_cfg = provider_config
                providers.append(self._provider_factory.build(key, provider_cfg))
        else:
            providers.append(self._provider_factory.build("native"))

        return ToolExecutor(
            providers=providers,
            allowlist=tools_config.allowlist,
            policies=config.policies,
            observability=config.observability,
            emit_event=emit_event,
        )


__all__ = ["EngineFactory", "ModelFactory", "ToolProviderFactory", "ToolExecutorFactory"]
