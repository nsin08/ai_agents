"""Tests for tool contract definitions."""

from __future__ import annotations

import pytest

from agent_core.tools import RiskLevel, ToolContract, ToolIdempotency


def test_tool_contract_requires_idempotency_for_write() -> None:
    with pytest.raises(ValueError, match="idempotency"):
        ToolContract(
            name="write_tool",
            description="Writes data.",
            risk=RiskLevel.WRITE,
        )


def test_tool_contract_accepts_idempotent_write() -> None:
    contract = ToolContract(
        name="write_tool",
        description="Writes data.",
        risk=RiskLevel.WRITE,
        idempotency=ToolIdempotency(required=True, key_field="request_id"),
    )

    assert contract.idempotency.required
    assert contract.idempotency.key_field == "request_id"
