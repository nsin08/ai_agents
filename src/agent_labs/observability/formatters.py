"""
Log formatters for structured logging.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonFormatter:
    """Format log records as JSON."""

    def format(self, record: Dict[str, Any]) -> str:
        record = dict(record)
        record.setdefault("timestamp", _utc_timestamp())
        return json.dumps(record, sort_keys=True)


class TextFormatter:
    """Format log records as human-readable text."""

    def format(self, record: Dict[str, Any]) -> str:
        record = dict(record)
        timestamp = record.get("timestamp", _utc_timestamp())
        level = record.get("level", "INFO")
        message = record.get("message", "")
        step = record.get("step", "")
        suffix = f" step={step}" if step else ""
        return f"{timestamp} [{level}] {message}{suffix}"
