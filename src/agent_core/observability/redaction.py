"""Redaction utilities for observability."""

from __future__ import annotations

from typing import Any, Mapping

from ..config.models import RedactConfig


_SECRET_KEYS = ("secret", "token", "api_key", "apikey", "password", "authorization", "auth", "bearer", "key")
_PII_KEYS = ("email", "phone", "ssn", "social", "name", "address")


class Redactor:
    def __init__(self, config: RedactConfig | None = None) -> None:
        self._config = config or RedactConfig()

    def redact(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._redact_value(payload) if isinstance(payload, Mapping) else {"value": payload}

    def _redact_value(self, value: Any, key: str | None = None) -> Any:
        if isinstance(value, Mapping):
            return {k: self._redact_value(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact_value(item, key) for item in value]
        if key and isinstance(value, str):
            lowered = key.lower()
            if self._config.secrets and any(token in lowered for token in _SECRET_KEYS):
                return "<redacted>"
            if self._config.pii and any(token in lowered for token in _PII_KEYS):
                return "<redacted>"
        return value


__all__ = ["Redactor"]
