"""
Built-in guardrails for safety enforcement.
"""

from __future__ import annotations

import re
from typing import List

from .base import Guardrail, GuardrailResult
from ..context.tokens import TokenCounter


class TokenLimitGuardrail(Guardrail):
    """Prevents context overflow by enforcing a token limit."""

    name = "token_limit"

    def __init__(self, max_tokens: int, enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.max_tokens = max_tokens

    def check_input(self, text: str) -> GuardrailResult:
        tokens = TokenCounter.count(text)
        if tokens > self.max_tokens:
            return GuardrailResult(
                allowed=False,
                reason="Input exceeds token limit",
                details={"tokens": tokens, "max_tokens": self.max_tokens},
            )
        return GuardrailResult(
            allowed=True,
            details={"tokens": tokens, "max_tokens": self.max_tokens},
        )

    def check_output(self, text: str) -> GuardrailResult:
        tokens = TokenCounter.count(text)
        if tokens > self.max_tokens:
            return GuardrailResult(
                allowed=False,
                reason="Output exceeds token limit",
                details={"tokens": tokens, "max_tokens": self.max_tokens},
            )
        return GuardrailResult(
            allowed=True,
            details={"tokens": tokens, "max_tokens": self.max_tokens},
        )

    def check_tool(self, tool_name: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)


class ToolAllowlistGuardrail(Guardrail):
    """Restricts tool usage to an allowlist."""

    name = "tool_allowlist"

    def __init__(self, allowed_tools: List[str], enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.allowed_tools = set(allowed_tools)

    def check_input(self, text: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)

    def check_output(self, text: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)

    def check_tool(self, tool_name: str) -> GuardrailResult:
        if tool_name not in self.allowed_tools:
            return GuardrailResult(
                allowed=False,
                reason="Tool not in allowlist",
                details={"tool": tool_name, "allowed_tools": sorted(self.allowed_tools)},
            )
        return GuardrailResult(allowed=True)


class InputValidationGuardrail(Guardrail):
    """Rejects inputs that match blocked patterns or exceed length."""

    name = "input_validation"

    def __init__(
        self,
        max_input_length: int = 1000,
        patterns_to_block: List[str] | None = None,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.max_input_length = max_input_length
        self.patterns_to_block = patterns_to_block or []

    def check_input(self, text: str) -> GuardrailResult:
        if len(text) > self.max_input_length:
            return GuardrailResult(
                allowed=False,
                reason="Input exceeds max length",
                details={"length": len(text), "max_input_length": self.max_input_length},
            )
        for pattern in self.patterns_to_block:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return GuardrailResult(
                    allowed=False,
                    reason="Input matched blocked pattern",
                    details={"pattern": pattern},
                )
        return GuardrailResult(allowed=True)

    def check_output(self, text: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)

    def check_tool(self, tool_name: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)


class OutputFilterGuardrail(Guardrail):
    """Sanitizes outputs by blocking or redacting patterns."""

    name = "output_filter"

    def __init__(
        self,
        patterns_to_block: List[str] | None = None,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.patterns_to_block = patterns_to_block or []

    def check_input(self, text: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)

    def check_output(self, text: str) -> GuardrailResult:
        sanitized = text
        for pattern in self.patterns_to_block:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        return GuardrailResult(
            allowed=True,
            reason="Output sanitized" if sanitized != text else "",
            sanitized_output=sanitized,
        )

    def check_tool(self, tool_name: str) -> GuardrailResult:
        return GuardrailResult(allowed=True)
