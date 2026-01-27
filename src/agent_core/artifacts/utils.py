"""Utilities for artifact bundle generation."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from ..config.models import RedactConfig
from ..observability import Redactor, utc_now


DETERMINISTIC_TIME = "1970-01-01T00:00:00+00:00"


def redact_config_snapshot(config: Mapping[str, Any]) -> dict[str, Any]:
    redactor = Redactor(RedactConfig(pii=True, secrets=True))
    return redactor.redact(config)


def hash_config_snapshot(snapshot: Mapping[str, Any]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def normalize_events_for_determinism(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trace_map: dict[str, str] = {}
    span_map: dict[str, str] = {}
    trace_counter = 0
    span_counter = 0
    normalized: list[dict[str, Any]] = []

    for event in events:
        item = json.loads(json.dumps(event, default=str))
        item["time"] = DETERMINISTIC_TIME
        attrs = item.get("attrs", {})
        if isinstance(attrs, dict):
            if "latency_s" in attrs:
                attrs["latency_s"] = 0
            usage = attrs.get("usage")
            if isinstance(usage, dict):
                if "latency_s" in usage:
                    usage["latency_s"] = 0
                if "cost" in usage:
                    usage["cost"] = 0
                attrs["usage"] = usage
            item["attrs"] = attrs
        trace = item.get("trace")
        if isinstance(trace, dict):
            trace_id = trace.get("trace_id")
            if trace_id:
                if trace_id not in trace_map:
                    trace_counter += 1
                    trace_map[trace_id] = f"trace-{trace_counter}"
                trace["trace_id"] = trace_map[trace_id]
            span_id = trace.get("span_id")
            if span_id:
                if span_id not in span_map:
                    span_counter += 1
                    span_map[span_id] = f"span-{span_counter}"
                trace["span_id"] = span_map[span_id]
            parent_span_id = trace.get("parent_span_id")
            if parent_span_id:
                if parent_span_id not in span_map:
                    span_counter += 1
                    span_map[parent_span_id] = f"span-{span_counter}"
                trace["parent_span_id"] = span_map[parent_span_id]
            item["trace"] = trace
        normalized.append(item)

    return normalized


def normalize_tool_calls_for_determinism(tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in tool_calls:
        item = json.loads(json.dumps(entry, default=str))
        if "time" in item:
            item["time"] = DETERMINISTIC_TIME
        normalized.append(item)
    return normalized


def deterministic_time() -> str:
    return DETERMINISTIC_TIME


__all__ = [
    "DETERMINISTIC_TIME",
    "deterministic_time",
    "hash_config_snapshot",
    "normalize_events_for_determinism",
    "normalize_tool_calls_for_determinism",
    "redact_config_snapshot",
    "utc_now",
]
