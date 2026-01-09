"""
Unit tests for safety guardrails.
"""

import json
import pytest
from tempfile import NamedTemporaryFile

from src.agent_labs.safety import (
    TokenLimitGuardrail,
    ToolAllowlistGuardrail,
    InputValidationGuardrail,
    OutputFilterGuardrail,
    SafetyChecker,
    SafetyViolation,
    load_config,
    build_guardrails,
)


def test_token_limit_guardrail_blocks_large_input():
    guardrail = TokenLimitGuardrail(max_tokens=2)
    result = guardrail.check_input("one two three")
    assert result.allowed is False


def test_tool_allowlist_guardrail_blocks_unknown_tool():
    guardrail = ToolAllowlistGuardrail(allowed_tools=["calculator"])
    result = guardrail.check_tool("web_search")
    assert result.allowed is False


def test_input_validation_guardrail_blocks_pattern():
    guardrail = InputValidationGuardrail(patterns_to_block=["DROP TABLE"])
    result = guardrail.check_input("please drop table users")
    assert result.allowed is False


def test_output_filter_guardrail_sanitizes():
    guardrail = OutputFilterGuardrail(patterns_to_block=["secret"])
    result = guardrail.check_output("my secret key")
    assert result.allowed is True
    assert "[REDACTED]" in result.sanitized_output


def test_safety_checker_raises_violation():
    guardrail = ToolAllowlistGuardrail(allowed_tools=["calculator"])
    checker = SafetyChecker(guardrails=[guardrail])
    with pytest.raises(SafetyViolation):
        checker.check_tool("web_search")


def test_safety_checker_sanitizes_output():
    guardrail = OutputFilterGuardrail(patterns_to_block=["secret"])
    checker = SafetyChecker(guardrails=[guardrail])
    output = checker.check_output("secret data")
    assert "[REDACTED]" in output


def test_config_load_json_and_build_guardrails():
    config = {
        "guardrails": {
            "token_limit": {"enabled": True, "max_tokens": 10},
            "tool_allowlist": {"enabled": True, "allowed_tools": ["calculator"]},
            "input_validation": {"enabled": True, "max_input_length": 50, "patterns_to_block": ["rm -rf"]},
            "output_filter": {"enabled": True, "patterns_to_block": ["secret"]},
        }
    }
    with NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(config, handle)
        path = handle.name

    loaded = load_config(path)
    guardrails = build_guardrails(loaded)
    assert len(guardrails) == 4


def test_config_load_yaml_and_build_guardrails():
    yaml = pytest.importorskip("yaml")
    config = {
        "guardrails": {
            "token_limit": {"enabled": True, "max_tokens": 5},
        }
    }
    with NamedTemporaryFile("w", suffix=".yaml", delete=False) as handle:
        yaml.safe_dump(config, handle)
        path = handle.name

    loaded = load_config(path)
    guardrails = build_guardrails(loaded)
    assert len(guardrails) == 1
