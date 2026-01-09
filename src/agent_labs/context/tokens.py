"""
Token counting utilities.
"""

from __future__ import annotations


class TokenCounter:
    """Model-agnostic token estimation."""

    TOKENS_PER_WORD = 1.3

    @staticmethod
    def count(text: str) -> int:
        if not text:
            return 0
        words = len(text.split())
        special_chars = sum(1 for c in text if c in ".,!?;:'\"()[]{}")
        return max(1, int(words * TokenCounter.TOKENS_PER_WORD + special_chars * 0.5))

    @classmethod
    def fits(cls, text: str, max_tokens: int) -> bool:
        return cls.count(text) <= max_tokens


def estimate_tokens(text: str, tokens_per_word: float = TokenCounter.TOKENS_PER_WORD) -> int:
    """Estimate tokens using a model-agnostic heuristic."""
    if tokens_per_word == TokenCounter.TOKENS_PER_WORD:
        return TokenCounter.count(text)
    if not text:
        return 0
    words = text.split()
    return max(1, int(len(words) * tokens_per_word))
