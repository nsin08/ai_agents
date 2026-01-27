"""Public API for agent_core."""

from __future__ import annotations

import asyncio
import os
from importlib import metadata
from typing import Any, Callable, Mapping

from .artifacts import (
    ArtifactPaths,
    ArtifactPayloads,
    deterministic_time,
    LocalFilesystemStore,
    RunArtifact,
    hash_config_snapshot,
    normalize_events_for_determinism,
    normalize_tool_calls_for_determinism,
    redact_config_snapshot,
    utc_now,
)
from .config import AgentCoreConfig, load_config
from .engine import EngineComponents, RunRequest, RunResult, RunStatus
from .factories import EngineFactory, ModelFactory, ToolExecutorFactory
from .memory import InMemorySessionStore, SessionStore
from .observability import MemoryExporter, ObservabilityEmitter, Redactor, build_emitter
from .registry import AgentCoreRegistry, get_global_registry
from .tools import ToolExecutor


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
        if emit_event is None:
            emitter = build_emitter(config.observability, self.registry.exporters)
            self._emit_event = emitter.emit if emitter else None
        else:
            self._emit_event = emit_event

        self._model_factory = ModelFactory(self.registry.model_providers)
        self._tool_factory = ToolExecutorFactory(self.registry.tool_providers)
        self._engine_factory = EngineFactory(self.registry.engines)

        self._models = models or self._model_factory.build_role_map(config.models.roles)
        self._tool_executor = tool_executor or self._tool_factory.build(config, emit_event=self._emit_event)
        self._engine = engine or self._engine_factory.build_with_config(
            config,
            tool_executor_factory=_FixedToolExecutorFactory(self._tool_executor),
            emit_event=self._emit_event,
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
        started_at = utc_now()
        memory_exporter = MemoryExporter()
        redactor = Redactor(self.config.observability.redact)
        memory_emitter = ObservabilityEmitter([memory_exporter], redactor=redactor)

        def emit(event: Mapping[str, Any]) -> None:
            memory_emitter.emit(event)
            if self._emit_event:
                self._emit_event(event)

        components = EngineComponents(
            models=self._models,
            tool_executor=self._tool_executor,
            memory=self._memory_factory(),
            policies=self.config.policies,
            emit_event=emit,
        )
        result = await self._engine.execute(request, components)
        finished_at = utc_now()

        config_snapshot = redact_config_snapshot(self.config.model_dump())
        config_hash = hash_config_snapshot(config_snapshot)
        events = list(memory_exporter.events)
        tool_calls = _collect_tool_calls(events, redactor)

        if self.config.mode == "deterministic":
            started_at = finished_at = deterministic_time()
            events = normalize_events_for_determinism(events)
            tool_calls = normalize_tool_calls_for_determinism(tool_calls)

        artifact = RunArtifact(
            run_id=request.run_id,
            status=_map_run_status(result.status),
            started_at=started_at,
            finished_at=finished_at,
            config_hash=config_hash,
            paths=ArtifactPaths(),
            versions=_collect_versions(),
            result={"status": result.status.value, "output_text": result.output_text},
            error=_result_error(result),
        )

        store = _build_artifact_store(self.config)
        payloads = ArtifactPayloads(
            config_snapshot=config_snapshot,
            events=events,
            tool_calls=tool_calls,
        )
        store.save_artifact(artifact, payloads)
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


def _map_run_status(status: RunStatus) -> str:
    if status == RunStatus.SUCCESS:
        return "finished"
    if status == RunStatus.CANCELLED:
        return "canceled"
    return "failed"


def _collect_versions() -> dict[str, Any]:
    versions: dict[str, Any] = {}
    try:
        versions["ai_agents"] = metadata.version("ai_agents")
    except metadata.PackageNotFoundError:
        versions["ai_agents"] = "unknown"
    git_commit = os.getenv("GIT_COMMIT")
    if git_commit:
        versions["git_commit"] = git_commit
    return versions


def _result_error(result: RunResult) -> dict[str, Any] | None:
    if result.status == RunStatus.SUCCESS:
        return None
    return {
        "type": result.status.value,
        "message": result.reason or "",
    }


def _collect_tool_calls(events: list[dict[str, Any]], redactor: Redactor) -> list[dict[str, Any]]:
    tool_calls: list[dict[str, Any]] = []
    for event in events:
        if event.get("event_type") not in {"tool.call.finished", "tool.call.blocked"}:
            continue
        attrs = event.get("attrs") or {}
        summary = {
            "run_id": event.get("run_id"),
            "tool_name": attrs.get("tool_name"),
            "tool_call_id": attrs.get("tool_call_id"),
            "status": attrs.get("status"),
            "arguments": attrs.get("arguments"),
            "output": attrs.get("output"),
            "error": attrs.get("error"),
        }
        tool_calls.append(redactor.redact(summary))
    return tool_calls


def _build_artifact_store(config: AgentCoreConfig) -> LocalFilesystemStore:
    store_cfg = config.artifacts.store
    base_dir = ""
    if isinstance(store_cfg.config, dict):
        base_dir = str(store_cfg.config.get("base_dir") or "").strip()
    if not base_dir:
        base_dir = "artifacts"
    return LocalFilesystemStore(base_dir=base_dir)


__all__ = ["AgentCore", "RunArtifact"]
