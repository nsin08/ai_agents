"""Public API for agent_core."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .config import AgentCoreConfig, load_config
from .engine import EngineComponents, RunRequest, RunResult
from .factories import EngineFactory, ModelFactory, ToolExecutorFactory
from .memory import InMemorySessionStore, SessionStore
from .registry import AgentCoreRegistry, get_global_registry
from .tools import ToolExecutor


@dataclass(frozen=True)
class RunArtifact:
    run_id: str
    config_snapshot: dict[str, Any]
    request: RunRequest
    result: RunResult
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentCore:
    """Primary user entry point for agent_core."""

    def __init__(
        self,
        config: AgentCoreConfig,
        *,
        registry: AgentCoreRegistry | None = None,
        engine: Any | None = None,
        models: Mapping[str, Any] | None = None,
        tool_executor: ToolExecutor | None = None,
        memory_factory: Callable[[], SessionStore] | None = None,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> None:
        self.config = config
        self.registry = registry or get_global_registry()
        self._emit_event = emit_event

        self._model_factory = ModelFactory(self.registry.model_providers)
        self._tool_factory = ToolExecutorFactory(self.registry.tool_providers)
        self._engine_factory = EngineFactory(self.registry.engines)

        self._models = models or self._model_factory.build_role_map(config.models.roles)
        self._tool_executor = tool_executor or self._tool_factory.build(config, emit_event=emit_event)
        self._engine = engine or self._engine_factory.build_with_config(
            config,
            tool_executor_factory=_FixedToolExecutorFactory(self._tool_executor),
            emit_event=emit_event,
        )

        self._memory_factory = memory_factory or self._default_memory_factory

    @classmethod
    def from_file(
        cls,
        path: str,
        *,
        registry: AgentCoreRegistry | None = None,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> "AgentCore":
        config = load_config(path=path)
        return cls(config, registry=registry, emit_event=emit_event)

    @classmethod
    def from_env(
        cls,
        *,
        registry: AgentCoreRegistry | None = None,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> "AgentCore":
        config = load_config()
        return cls(config, registry=registry, emit_event=emit_event)

    @classmethod
    def from_config(
        cls,
        config: AgentCoreConfig,
        *,
        registry: AgentCoreRegistry | None = None,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> "AgentCore":
        return cls(config, registry=registry, emit_event=emit_event)

    async def run(self, request: RunRequest) -> RunResult:
        components = EngineComponents(
            models=self._models,
            tool_executor=self._tool_executor,
            memory=self._memory_factory(),
            policies=self.config.policies,
            emit_event=self._emit_event,
        )
        return await self._engine.execute(request, components)

    async def run_with_artifacts(self, request: RunRequest) -> tuple[RunResult, RunArtifact]:
        result = await self.run(request)
        artifact = RunArtifact(
            run_id=request.run_id,
            config_snapshot=self.config.model_dump(),
            request=request,
            result=result,
        )
        return result, artifact

    def run_sync(self, request: RunRequest) -> RunResult:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.run(request))
        raise RuntimeError("run_sync cannot be called from a running event loop; use await run().")

    @staticmethod
    def _default_memory_factory() -> SessionStore:
        return InMemorySessionStore()


class _FixedToolExecutorFactory:
    def __init__(self, tool_executor: ToolExecutor) -> None:
        self._tool_executor = tool_executor

    def build(
        self,
        config: AgentCoreConfig,
        emit_event: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> ToolExecutor:
        return self._tool_executor


__all__ = ["AgentCore", "RunArtifact"]
