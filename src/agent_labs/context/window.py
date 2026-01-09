"""
Context window management for token budgeting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .tokens import TokenCounter
from .templates import ContextSummarizer


@dataclass
class ContextWindow:
    """Track token usage and available space."""

    max_tokens: int
    overflow_strategy: str = "error"
    summarizer: Optional[ContextSummarizer] = None
    token_usage: int = 0
    items: List[dict] = field(default_factory=list)

    def available_tokens(self) -> int:
        return max(0, self.max_tokens - self.token_usage)

    def fits(self, text: str) -> bool:
        return TokenCounter.count(text) <= self.available_tokens()

    async def add(self, text: str, metadata: Optional[dict] = None) -> bool:
        tokens_needed = TokenCounter.count(text)
        available = self.available_tokens()

        if tokens_needed <= available:
            self.items.append({"text": text, "metadata": metadata or {}})
            self.token_usage += tokens_needed
            return True

        if self.overflow_strategy == "error":
            raise TokenLimitExceededError(
                f"Text requires {tokens_needed} tokens, only {available} available"
            )

        if self.overflow_strategy == "drop":
            if self.items:
                old = self.items.pop(0)
                self.token_usage -= TokenCounter.count(old["text"])
                return await self.add(text, metadata)
            raise TokenLimitExceededError("Cannot fit text even with oldest removed")

        if self.overflow_strategy == "summarize":
            if not self.summarizer:
                raise TokenLimitExceededError("Summarizer required for summarize strategy")
            if self.items:
                old = self.items.pop(0)
                old_text = old["text"]
                self.token_usage -= TokenCounter.count(old_text)
                target_tokens = max(1, TokenCounter.count(old_text) // 2)
                summarized = await self.summarizer.summarize(old_text, max_length=target_tokens)
                self.items.insert(0, {"text": summarized, "metadata": old["metadata"]})
                self.token_usage += TokenCounter.count(summarized)
                return await self.add(text, metadata)
            raise TokenLimitExceededError("Cannot fit text even with summarization")

        raise ValueError(f"Unknown overflow strategy: {self.overflow_strategy}")


class TokenLimitExceededError(RuntimeError):
    """Raised when text cannot fit into the context window."""
