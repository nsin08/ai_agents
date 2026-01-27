"""Tests for artifact redaction utilities."""

from __future__ import annotations

from agent_core.artifacts import redact_config_snapshot


def test_redact_config_snapshot_masks_secrets() -> None:
    snapshot = {
        "models": {"roles": {"actor": {"api_key": "secret", "model": "x"}}},
        "service": {"auth": {"token": "token-value"}},
    }

    redacted = redact_config_snapshot(snapshot)

    assert redacted["models"]["roles"]["actor"]["api_key"] == "<redacted>"
    assert redacted["service"]["auth"]["token"] == "<redacted>"
