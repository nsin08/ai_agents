"""Tool contracts and execution results for agent_core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Sequence
from uuid import uuid4


class ExecutionStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"


class RiskLevel(StrEnum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class ToolIdempotency:
    required: bool = False
    key_field: str | None = None


@dataclass
class ToolDataHandling:
    pii: bool = False
    secrets: bool = False


@dataclass
class ToolConstraints:
    requires_network: bool = False
    requires_file_access: bool = False
    requires_write: bool = False
    max_runtime_ms: int = 0


@dataclass
class ToolPermissions:
    read_paths: list[str] = field(default_factory=list)
    write_paths: list[str] = field(default_factory=list)


@dataclass
class ToolContract:
    name: str
    description: str
    version: str = "1.0.0"
    risk: RiskLevel | str = RiskLevel.READ
    input_schema: Mapping[str, Any] = field(default_factory=dict)
    output_schema: Mapping[str, Any] | None = None
    required_scopes: list[str] = field(default_factory=list)
    idempotency: ToolIdempotency = field(default_factory=ToolIdempotency)
    data_handling: ToolDataHandling = field(default_factory=ToolDataHandling)
    constraints: ToolConstraints = field(default_factory=ToolConstraints)
    permissions: ToolPermissions = field(default_factory=ToolPermissions)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("ToolContract.name must be set.")
        if not self.description:
            raise ValueError("ToolContract.description must be set.")
        if isinstance(self.risk, str):
            self.risk = RiskLevel(self.risk)
        if self.risk in {RiskLevel.WRITE, RiskLevel.ADMIN} and not self.idempotency.required:
            raise ValueError("Write/admin tools must declare idempotency.required=True.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "risk": self.risk.value if isinstance(self.risk, RiskLevel) else str(self.risk),
            "input_schema": dict(self.input_schema),
            "output_schema": dict(self.output_schema) if self.output_schema is not None else None,
            "required_scopes": list(self.required_scopes),
            "idempotency": {
                "required": self.idempotency.required,
                "key_field": self.idempotency.key_field,
            },
            "data_handling": {
                "pii": self.data_handling.pii,
                "secrets": self.data_handling.secrets,
            },
            "constraints": {
                "requires_network": self.constraints.requires_network,
                "requires_file_access": self.constraints.requires_file_access,
                "requires_write": self.constraints.requires_write,
                "max_runtime_ms": self.constraints.max_runtime_ms,
            },
            "permissions": {
                "read_paths": list(self.permissions.read_paths),
                "write_paths": list(self.permissions.write_paths),
            },
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ToolContract":
        idempotency_payload = payload.get("idempotency") or {}
        data_handling_payload = payload.get("data_handling") or {}
        constraints_payload = payload.get("constraints") or {}
        permissions_payload = payload.get("permissions") or {}
        return cls(
            name=str(payload.get("name", "")).strip(),
            description=str(payload.get("description", "")).strip(),
            version=str(payload.get("version", "1.0.0")).strip() or "1.0.0",
            risk=payload.get("risk", RiskLevel.READ),
            input_schema=payload.get("input_schema") or {},
            output_schema=payload.get("output_schema"),
            required_scopes=list(payload.get("required_scopes") or []),
            idempotency=ToolIdempotency(
                required=bool(idempotency_payload.get("required", False)),
                key_field=idempotency_payload.get("key_field"),
            ),
            data_handling=ToolDataHandling(
                pii=bool(data_handling_payload.get("pii", False)),
                secrets=bool(data_handling_payload.get("secrets", False)),
            ),
            constraints=ToolConstraints(
                requires_network=bool(constraints_payload.get("requires_network", False)),
                requires_file_access=bool(constraints_payload.get("requires_file_access", False)),
                requires_write=bool(constraints_payload.get("requires_write", False)),
                max_runtime_ms=int(constraints_payload.get("max_runtime_ms", 0) or 0),
            ),
            permissions=ToolPermissions(
                read_paths=list(permissions_payload.get("read_paths") or []),
                write_paths=list(permissions_payload.get("write_paths") or []),
            ),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass
class TraceContext:
    trace_id: str
    span_id: str
    parent_span_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
        }


@dataclass
class ToolCall:
    tool_name: str
    arguments: Mapping[str, Any]
    tool_call_id: str = field(default_factory=lambda: uuid4().hex)
    run_id: str | None = None
    timeout_ms: int | None = None
    trace: TraceContext | None = None
    scopes: Sequence[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": dict(self.arguments),
            "tool_call_id": self.tool_call_id,
            "run_id": self.run_id,
            "timeout_ms": self.timeout_ms,
            "trace": self.trace.to_dict() if self.trace else None,
            "scopes": list(self.scopes) if self.scopes is not None else None,
        }


@dataclass
class ToolError:
    type: str
    message: str
    details: dict[str, Any] | None = None
    retryable: bool = False
    source: str = "tool"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "message": self.message,
            "details": dict(self.details) if self.details else None,
            "retryable": self.retryable,
            "source": self.source,
        }


@dataclass
class ToolResult:
    status: ExecutionStatus
    output: Any = None
    error: ToolError | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    tool_call_id: str | None = None
    tool_name: str | None = None
    trace: TraceContext | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error.to_dict() if self.error else None,
            "duration_ms": self.duration_ms,
            "metadata": dict(self.metadata),
            "tool_call_id": self.tool_call_id,
            "tool_name": self.tool_name,
            "trace": self.trace.to_dict() if self.trace else None,
            "timestamp": self.timestamp,
        }


__all__ = [
    "ExecutionStatus",
    "RiskLevel",
    "ToolCall",
    "ToolConstraints",
    "ToolContract",
    "ToolDataHandling",
    "ToolError",
    "ToolIdempotency",
    "ToolPermissions",
    "ToolResult",
    "TraceContext",
]
