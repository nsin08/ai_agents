"""Execution engines for agent_core."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Mapping, Protocol
from uuid import uuid4

from .config.models import PoliciesConfig
from .memory import InMemorySessionStore, SessionStore
from .model import ModelClient, ModelResponse
from .observability import TraceContext, utc_now
from .tools import ToolExecutor
from .tools import ToolCall as ToolExecutorCall


class RunStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BUDGET_EXCEEDED = "budget_exceeded"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class RunRequest:
    input: str
    run_id: str = field(default_factory=lambda: uuid4().hex)
    max_turns: int = 5
    timeout_s: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    cancel_event: asyncio.Event | None = None


@dataclass
class RunResult:
    status: RunStatus
    output_text: str = ""
    turns: int = 0
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineComponents:
    models: Mapping[str, ModelClient]
    tool_executor: ToolExecutor | None = None
    memory: SessionStore | None = None
    policies: PoliciesConfig | None = None
    emit_event: Callable[[Mapping[str, Any]], None] | None = None


class ExecutionEngine(Protocol):
    async def execute(self, request: RunRequest, components: EngineComponents) -> RunResult:
        ...


class LocalEngine:
    """Local execution engine with a simple state machine."""

    def __init__(self, tool_executor: ToolExecutor | None = None) -> None:
        self._state = "initialize"
        self.tool_executor = tool_executor

    async def execute(self, request: RunRequest, components: EngineComponents) -> RunResult:
        policies = components.policies or PoliciesConfig()
        memory = components.memory or InMemorySessionStore()
        tool_executor = components.tool_executor or self.tool_executor
        models = components.models
        emit_event = components.emit_event

        start = time.perf_counter()
        total_tokens = 0
        turns = 0
        output_text = ""
        run_trace = TraceContext.new()

        if request.max_turns <= 0:
            return self._finalize_run(
                emit_event,
                request.run_id,
                run_trace,
                RunStatus.FAILED,
                "max_turns",
                output_text,
                turns,
            )

        await memory.add_message("user", request.input)
        self._emit_run_event(
            emit_event,
            request.run_id,
            run_trace,
            "run.started",
            "info",
            {"turns": 0},
        )
        self._emit(emit_event, request.run_id, "initialize", 0, RunStatus.SUCCESS)

        try:
            for turn in range(request.max_turns):
                turns = turn + 1
                early_exit = self._enforce_limits(
                    request,
                    policies,
                    start,
                    total_tokens,
                    turns,
                    output_text,
                    emit_event,
                    run_trace,
                )
                if early_exit:
                    return early_exit

                self._state = "observe"
                self._emit(emit_event, request.run_id, self._state, turns, RunStatus.SUCCESS)
                context = await memory.get_context()

                self._state = "plan"
                self._emit(emit_event, request.run_id, self._state, turns, RunStatus.SUCCESS)
                plan_trace = run_trace.child()
                plan_response = await self._call_model_raw(
                    models,
                    "planner",
                    context,
                    "Plan the next step.",
                    request.run_id,
                    emit_event,
                    plan_trace,
                )
                total_tokens += self._tokens_from_response(plan_response)
                if plan_response.text:
                    await memory.add_message("assistant", plan_response.text, metadata={"type": "plan"})
                early_exit = self._enforce_limits(
                    request,
                    policies,
                    start,
                    total_tokens,
                    turns,
                    output_text,
                    emit_event,
                    run_trace,
                )
                if early_exit:
                    return early_exit

                self._state = "act"
                self._emit(emit_event, request.run_id, self._state, turns, RunStatus.SUCCESS)
                actor_trace = run_trace.child()
                model_response = await self._call_model_raw(
                    models,
                    "actor",
                    await memory.get_context(),
                    "",
                    request.run_id,
                    emit_event,
                    actor_trace,
                )
                total_tokens += self._tokens_from_response(model_response)
                if model_response.text:
                    await memory.add_message("assistant", model_response.text, metadata={"type": "act"})
                    output_text = model_response.text
                early_exit = self._enforce_limits(
                    request,
                    policies,
                    start,
                    total_tokens,
                    turns,
                    output_text,
                    emit_event,
                    run_trace,
                )
                if early_exit:
                    return early_exit
                tool_calls = model_response.tool_calls or []
                if tool_calls and tool_executor is None:
                    return self._finalize_run(
                        emit_event,
                        request.run_id,
                        run_trace,
                        RunStatus.FAILED,
                        "tool_executor_missing",
                        output_text,
                        turns,
                    )

                if tool_calls:
                    for call in tool_calls:
                        early_exit = self._enforce_limits(
                            request,
                            policies,
                            start,
                            total_tokens,
                            turns,
                            output_text,
                            emit_event,
                            run_trace,
                        )
                        if early_exit:
                            return early_exit
                        tool_trace = TraceContext(
                            trace_id=run_trace.trace_id,
                            span_id=uuid4().hex,
                            parent_span_id=actor_trace.span_id,
                        )
                        tool_kwargs = {
                            "tool_name": call.name,
                            "arguments": call.arguments,
                            "run_id": request.run_id,
                            "trace": tool_trace,
                        }
                        if call.call_id:
                            tool_kwargs["tool_call_id"] = call.call_id
                        result = await tool_executor.execute(ToolExecutorCall(**tool_kwargs))
                        tool_payload: Any = result.output
                        if result.error:
                            tool_payload = {"output": result.output, "error": result.error.to_dict()}
                        await memory.add_message(
                            "tool",
                            json.dumps(tool_payload, default=str) if tool_payload is not None else "",
                            name=call.name,
                            tool_call_id=call.call_id,
                            metadata={"status": result.status.value},
                        )

                    followup_trace = run_trace.child()
                    followup_response = await self._call_model_raw(
                        models,
                        "actor",
                        await memory.get_context(),
                        "Provide final answer.",
                        request.run_id,
                        emit_event,
                        followup_trace,
                    )
                    total_tokens += self._tokens_from_response(followup_response)
                    output_text = followup_response.text
                    if followup_response.text:
                        await memory.add_message("assistant", followup_response.text, metadata={"type": "final"})
                    early_exit = self._enforce_limits(
                        request,
                        policies,
                        start,
                        total_tokens,
                        turns,
                        output_text,
                        emit_event,
                        run_trace,
                    )
                    if early_exit:
                        return early_exit
                else:
                    output_text = model_response.text

                self._state = "verify"
                self._emit(emit_event, request.run_id, self._state, turns, RunStatus.SUCCESS)
                if "critic" in models:
                    critic_trace = run_trace.child()
                    verdict_response = await self._call_model_raw(
                        models,
                        "critic",
                        await memory.get_context(),
                        "Answer YES if complete, otherwise NO with reason.",
                        request.run_id,
                        emit_event,
                        critic_trace,
                    )
                    total_tokens += self._tokens_from_response(verdict_response)
                    if verdict_response.text:
                        await memory.add_message("assistant", verdict_response.text, metadata={"type": "verify"})
                    early_exit = self._enforce_limits(
                        request,
                        policies,
                        start,
                        total_tokens,
                        turns,
                        output_text,
                        emit_event,
                        run_trace,
                    )
                    if early_exit:
                        return early_exit
                    if verdict_response.text.strip().upper().startswith("YES"):
                        self._state = "done"
                        self._emit(emit_event, request.run_id, self._state, turns, RunStatus.SUCCESS)
                        return self._finalize_run(
                            emit_event,
                            request.run_id,
                            run_trace,
                            RunStatus.SUCCESS,
                            None,
                            output_text,
                            turns,
                        )
                else:
                    self._state = "done"
                    self._emit(emit_event, request.run_id, self._state, turns, RunStatus.SUCCESS)
                    return self._finalize_run(
                        emit_event,
                        request.run_id,
                        run_trace,
                        RunStatus.SUCCESS,
                        None,
                        output_text,
                        turns,
                    )

            return self._finalize_run(
                emit_event,
                request.run_id,
                run_trace,
                RunStatus.FAILED,
                "max_turns",
                output_text,
                turns,
            )
        except Exception as exc:  # pragma: no cover - safety net
            self._emit_run_event(
                emit_event,
                request.run_id,
                run_trace,
                "run.failed",
                "error",
                {"error": str(exc), "turns": turns},
            )
            raise

    @staticmethod
    def _timeout_exceeded(request: RunRequest, policies: PoliciesConfig, start: float) -> bool:
        timeout_s = request.timeout_s
        if policies.budgets.max_run_seconds:
            timeout_s = min(timeout_s or policies.budgets.max_run_seconds, policies.budgets.max_run_seconds)
        if not timeout_s:
            return False
        return (time.perf_counter() - start) >= timeout_s

    @staticmethod
    def _count_tokens(text: str | None) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    @classmethod
    def _tokens_from_response(cls, response: ModelResponse) -> int:
        usage = response.usage
        if usage:
            if usage.total_tokens is not None:
                return int(usage.total_tokens)
            prompt_tokens = usage.prompt_tokens or 0
            completion_tokens = usage.completion_tokens or 0
            if prompt_tokens or completion_tokens:
                return int(prompt_tokens + completion_tokens)
        return cls._count_tokens(response.text)

    @classmethod
    def _enforce_limits(
        cls,
        request: RunRequest,
        policies: PoliciesConfig,
        start: float,
        total_tokens: int,
        turns: int,
        output_text: str,
        emit_event: Callable[[Mapping[str, Any]], None] | None,
        run_trace: TraceContext,
    ) -> RunResult | None:
        if request.cancel_event and request.cancel_event.is_set():
            return cls._finalize_run(
                emit_event,
                request.run_id,
                run_trace,
                RunStatus.CANCELLED,
                "cancelled",
                output_text,
                turns,
            )
        if cls._timeout_exceeded(request, policies, start):
            return cls._finalize_run(
                emit_event,
                request.run_id,
                run_trace,
                RunStatus.TIMEOUT,
                "timeout",
                output_text,
                turns,
            )
        if policies.budgets.max_total_tokens and total_tokens >= policies.budgets.max_total_tokens:
            return cls._finalize_run(
                emit_event,
                request.run_id,
                run_trace,
                RunStatus.BUDGET_EXCEEDED,
                "token_budget",
                output_text,
                turns,
            )
        return None

    async def _call_model_raw(
        self,
        models: Mapping[str, ModelClient],
        role: str,
        context: list[dict[str, Any]],
        instruction: str,
        run_id: str,
        emit_event: Callable[[Mapping[str, Any]], None] | None,
        trace: TraceContext,
    ) -> ModelResponse:
        model = models.get(role) or models.get("actor")
        if model is None:
            raise ValueError(f"No model configured for role '{role}' and no actor fallback.")
        messages = list(context)
        if instruction:
            messages.append({"role": "user", "content": instruction})
        self._emit_run_event(
            emit_event,
            run_id,
            trace,
            "model.call.started",
            "info",
            {"role": role},
            actor="model",
        )
        start = time.perf_counter()
        try:
            response = await model.generate(messages, role=role)
        except Exception as exc:  # pragma: no cover - error path
            self._emit_run_event(
                emit_event,
                run_id,
                trace,
                "model.call.finished",
                "error",
                {"role": role, "error": str(exc)},
                actor="model",
            )
            raise
        duration = time.perf_counter() - start
        usage = response.usage
        usage_payload: dict[str, Any] = {}
        if usage:
            usage_payload = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "latency_s": usage.latency_s,
                "cost": usage.cost,
            }
        attrs = {"role": role, "latency_s": duration}
        if usage_payload:
            attrs["usage"] = usage_payload
        self._emit_run_event(
            emit_event,
            run_id,
            trace,
            "model.call.finished",
            "info",
            attrs,
            actor="model",
        )
        return response

    @classmethod
    def _finalize_run(
        cls,
        emit_event: Callable[[Mapping[str, Any]], None] | None,
        run_id: str,
        trace: TraceContext,
        status: RunStatus,
        reason: str | None,
        output_text: str,
        turns: int,
    ) -> RunResult:
        if status == RunStatus.SUCCESS:
            event_type = "run.finished"
            severity = "info"
        elif status == RunStatus.CANCELLED:
            event_type = "run.canceled"
            severity = "warn"
        else:
            event_type = "run.failed"
            severity = "error"
        cls._emit_run_event(
            emit_event,
            run_id,
            trace,
            event_type,
            severity,
            {"status": status.value, "reason": reason, "turns": turns},
        )
        return RunResult(
            status=status,
            output_text=output_text,
            turns=turns,
            reason=reason,
        )

    @staticmethod
    def _emit(
        emit_event: Callable[[Mapping[str, Any]], None] | None,
        run_id: str,
        state: str,
        turn: int,
        status: RunStatus,
    ) -> None:
        LocalEngine._emit_run_event(
            emit_event,
            run_id,
            None,
            "engine.state",
            "debug",
            {"state": state, "turn": turn, "status": status.value},
            actor="engine",
        )

    @staticmethod
    def _emit_run_event(
        emit_event: Callable[[Mapping[str, Any]], None] | None,
        run_id: str,
        trace: TraceContext | None,
        event_type: str,
        severity: str,
        attrs: Mapping[str, Any] | None = None,
        *,
        actor: str | None = "engine",
    ) -> None:
        if emit_event is None:
            return
        payload: dict[str, Any] = {
            "time": utc_now(),
            "run_id": run_id,
            "event_type": event_type,
            "severity": severity,
        }
        if trace is not None:
            payload["trace"] = trace.to_dict()
        if actor is not None:
            payload["actor"] = actor
        if attrs:
            payload["attrs"] = dict(attrs)
        emit_event(payload)


__all__ = [
    "ExecutionEngine",
    "EngineComponents",
    "LocalEngine",
    "RunRequest",
    "RunResult",
    "RunStatus",
]
