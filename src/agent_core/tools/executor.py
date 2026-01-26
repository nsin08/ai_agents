"""ToolExecutor: central enforcement point for tool calls."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from jsonschema import ValidationError, validate

from ..config.models import ObservabilityConfig, PoliciesConfig
from .contract import ExecutionStatus, ToolCall, ToolContract, ToolError, ToolResult
from .exceptions import (
    BudgetExceeded,
    PolicyViolation,
    ToolInputInvalid,
    ToolNotFound,
    ToolProviderError,
    ToolResultInvalid,
    ToolTimeout,
)
from .provider import ToolProvider


EventEmitter = Callable[[Mapping[str, Any]], None]


class ToolExecutor:
    """Validate, enforce policy, execute, and audit tool calls."""

    def __init__(
        self,
        providers: Sequence[ToolProvider],
        allowlist: Sequence[str] | None = None,
        policies: PoliciesConfig | None = None,
        observability: ObservabilityConfig | None = None,
        emit_event: EventEmitter | None = None,
    ) -> None:
        self._providers = list(providers)
        self._allowlist = set(allowlist or [])
        self._policies = policies or PoliciesConfig()
        self._observability = observability or ObservabilityConfig()
        self._emit_event = emit_event
        self._tool_index: dict[str, tuple[ToolProvider, ToolContract]] = {}
        self._call_counts: dict[str, int] = defaultdict(int)

    async def execute(self, call: ToolCall) -> ToolResult:
        tool_name = call.tool_name

        if not self._allowlist or tool_name not in self._allowlist:
            return self._blocked(
                call,
                PolicyViolation("Tool not allowlisted."),
            )

        budget_key = call.run_id or "default"
        max_calls = self._policies.budgets.max_tool_calls
        if max_calls and self._call_counts[budget_key] >= max_calls:
            return self._blocked(call, BudgetExceeded("Tool call budget exceeded."))

        provider, contract = await self._resolve_tool(tool_name)
        if provider is None or contract is None:
            return self._error_result(call, ToolNotFound(f"Tool '{tool_name}' not found."))

        if self._policies.read_only and (
            contract.risk.value in {"write", "admin"} or contract.constraints.requires_write
        ):
            return self._blocked(call, PolicyViolation("Tool blocked in read-only mode."))

        if contract.required_scopes:
            scopes = set(call.scopes or [])
            if not set(contract.required_scopes).issubset(scopes):
                return self._blocked(call, PolicyViolation("Missing required scopes."))

        try:
            self._validate_paths(contract, call.arguments)
        except PolicyViolation as exc:
            return self._blocked(call, exc)

        try:
            self._validate_schema(contract.input_schema, call.arguments, ToolInputInvalid)
        except ToolInputInvalid as exc:
            return self._error_result(call, exc, status=ExecutionStatus.INVALID_INPUT)

        self._call_counts[budget_key] += 1
        self._emit("tool.call.started", call, contract, status=ExecutionStatus.SUCCESS)

        timeout_s = self._timeout_seconds(call, contract)
        start = time.perf_counter()
        try:
            if timeout_s:
                result = await asyncio.wait_for(
                    provider.execute(tool_name, call.arguments),
                    timeout=timeout_s,
                )
            else:
                result = await provider.execute(tool_name, call.arguments)
        except asyncio.TimeoutError as exc:
            return self._error_result(call, ToolTimeout(str(exc)), status=ExecutionStatus.TIMEOUT)
        except ToolNotFound as exc:
            return self._error_result(call, exc, status=ExecutionStatus.NOT_FOUND)
        except ToolProviderError as exc:
            return self._error_result(call, exc)
        except Exception as exc:  # pragma: no cover - covered by provider tests
            return self._error_result(call, ToolProviderError(str(exc)))

        duration_ms = (time.perf_counter() - start) * 1000.0
        if not isinstance(result, ToolResult):
            result = ToolResult(status=ExecutionStatus.SUCCESS, output=result)
        normalized = self._normalize_result(call, contract, result, duration_ms)

        if normalized.status == ExecutionStatus.SUCCESS and contract.output_schema:
            try:
                self._validate_schema(contract.output_schema, normalized.output, ToolResultInvalid)
            except ToolResultInvalid as exc:
                normalized = self._error_result(call, exc, status=ExecutionStatus.FAILURE)

        self._emit(
            "tool.call.finished",
            call,
            contract,
            status=normalized.status,
            result=normalized,
        )
        return normalized

    async def execute_batch(self, calls: Sequence[ToolCall]) -> list[ToolResult]:
        results: list[ToolResult] = []
        for call in calls:
            results.append(await self.execute(call))
        return results

    async def _resolve_tool(
        self,
        tool_name: str,
    ) -> tuple[ToolProvider | None, ToolContract | None]:
        if tool_name in self._tool_index:
            return self._tool_index[tool_name][0], self._tool_index[tool_name][1]

        for provider in self._providers:
            contracts = await provider.list_tools()
            for contract in contracts:
                if contract.name not in self._tool_index:
                    self._tool_index[contract.name] = (provider, contract)

        entry = self._tool_index.get(tool_name)
        if entry is None:
            if not self._providers:
                return (None, None)
            return self._providers[0], None
        return entry

    def _timeout_seconds(self, call: ToolCall, contract: ToolContract) -> float | None:
        timeouts: list[float] = []
        if call.timeout_ms:
            timeouts.append(call.timeout_ms / 1000.0)
        if contract.constraints.max_runtime_ms:
            timeouts.append(contract.constraints.max_runtime_ms / 1000.0)
        if not timeouts:
            return None
        return min(timeouts)

    def _validate_schema(
        self,
        schema: Mapping[str, Any],
        payload: Any,
        error_cls: type[Exception],
    ) -> None:
        if not schema:
            return
        try:
            validate(instance=payload, schema=schema)
        except ValidationError as exc:
            raise error_cls(str(exc)) from exc

    def _validate_paths(self, contract: ToolContract, args: Mapping[str, Any]) -> None:
        if not contract.constraints.requires_file_access and not contract.permissions.read_paths:
            return
        allowed = [Path(path).resolve() for path in contract.permissions.read_paths]
        if not allowed:
            return
        raw_path = args.get("path")
        if raw_path is None:
            return
        candidate = Path(str(raw_path)).resolve()
        if not any(self._is_relative_to(candidate, root) for root in allowed):
            raise PolicyViolation("Path not permitted by tool contract.")

    @staticmethod
    def _is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def _normalize_result(
        self,
        call: ToolCall,
        contract: ToolContract,
        result: ToolResult,
        duration_ms: float,
    ) -> ToolResult:
        merged = ToolResult(
            status=result.status,
            output=result.output,
            error=result.error,
            duration_ms=duration_ms,
            metadata={**result.metadata, "tool_version": contract.version},
            tool_call_id=call.tool_call_id,
            tool_name=contract.name,
            trace=call.trace,
            timestamp=result.timestamp,
        )
        return merged

    def _error_result(
        self,
        call: ToolCall,
        exc: Exception,
        *,
        status: ExecutionStatus = ExecutionStatus.FAILURE,
    ) -> ToolResult:
        error = ToolError(
            type=getattr(exc, "error_type", exc.__class__.__name__),
            message=str(exc),
            retryable=getattr(exc, "retryable", False),
            source="policy" if isinstance(exc, (PolicyViolation, BudgetExceeded)) else "tool",
        )
        result = ToolResult(
            status=status,
            error=error,
            duration_ms=0.0,
            tool_call_id=call.tool_call_id,
            tool_name=call.tool_name,
            trace=call.trace,
        )
        self._emit(
            "tool.call.finished",
            call,
            None,
            status=status,
            result=result,
        )
        return result

    def _blocked(self, call: ToolCall, exc: Exception) -> ToolResult:
        error = ToolError(
            type=getattr(exc, "error_type", exc.__class__.__name__),
            message=str(exc),
            retryable=getattr(exc, "retryable", False),
            source="policy",
        )
        result = ToolResult(
            status=ExecutionStatus.FAILURE,
            error=error,
            duration_ms=0.0,
            tool_call_id=call.tool_call_id,
            tool_name=call.tool_name,
            trace=call.trace,
        )
        self._emit(
            "tool.call.blocked",
            call,
            None,
            status=ExecutionStatus.FAILURE,
            result=result,
        )
        return result

    def _emit(
        self,
        event_type: str,
        call: ToolCall,
        contract: ToolContract | None,
        *,
        status: ExecutionStatus,
        result: ToolResult | None = None,
    ) -> None:
        if self._emit_event is None:
            return
        redact = self._observability.redact
        attrs: dict[str, Any] = {
            "tool_name": call.tool_name,
            "tool_call_id": call.tool_call_id,
            "status": status.value,
        }
        if call.run_id:
            attrs["run_id"] = call.run_id
        if contract and (
            (redact.pii and contract.data_handling.pii)
            or (redact.secrets and contract.data_handling.secrets)
        ):
            attrs["arguments"] = "<redacted>"
            if result is not None:
                attrs["output"] = "<redacted>"
        else:
            attrs["arguments"] = dict(call.arguments)
            if result is not None:
                attrs["output"] = result.output

        if result and result.error:
            attrs["error"] = result.error.to_dict()

        payload = {
            "time": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "severity": "warn" if result and result.error else "info",
            "actor": "tool",
            "trace": call.trace.to_dict() if call.trace else None,
            "attrs": attrs,
        }
        self._emit_event(payload)


__all__ = ["ToolExecutor"]
