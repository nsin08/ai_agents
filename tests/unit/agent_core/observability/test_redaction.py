"""Tests for observability redaction."""

from __future__ import annotations

from agent_core.config.models import RedactConfig
from agent_core.observability import Redactor


def test_redaction_masks_sensitive_fields() -> None:
    redactor = Redactor(RedactConfig(pii=True, secrets=True))
    payload = {
        "attrs": {
            "api_key": "secret",
            "email": "user@example.com",
            "safe": "ok",
        }
    }

    redacted = redactor.redact(payload)

    assert redacted["attrs"]["api_key"] == "<redacted>"
    assert redacted["attrs"]["email"] == "<redacted>"
    assert redacted["attrs"]["safe"] == "ok"


def test_redaction_can_be_disabled() -> None:
    redactor = Redactor(RedactConfig(pii=False, secrets=False))
    payload = {"attrs": {"api_key": "secret"}}

    redacted = redactor.redact(payload)

    assert redacted["attrs"]["api_key"] == "secret"
