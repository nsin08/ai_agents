"""Context manifest types.

A context manifest describes what was included in a prompt and why. This is
useful for debugging, evaluation, and audit without logging raw sensitive text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ContextManifestItem:
    kind: str
    """Type of item (e.g., system, tool_schema, evidence, memory_fact, history)."""

    tokens: int
    """Estimated tokens for this item."""

    reason: str
    """Why this item was included (e.g., retrieval_top_k, high_confidence)."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Safe metadata (doc_id, chunk_id, tool name, keys). Avoid raw text."""


@dataclass
class ContextManifest:
    request_id: str
    max_tokens: int
    reserved_response_tokens: int
    items: List[ContextManifestItem] = field(default_factory=list)

    def add_item(
        self,
        *,
        kind: str,
        tokens: int,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.items.append(
            ContextManifestItem(
                kind=kind,
                tokens=tokens,
                reason=reason,
                metadata=metadata or {},
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "budget": {
                "max_tokens": self.max_tokens,
                "reserved_response_tokens": self.reserved_response_tokens,
            },
            "items": [
                {
                    "kind": item.kind,
                    "tokens": item.tokens,
                    "reason": item.reason,
                    "metadata": item.metadata,
                }
                for item in self.items
            ],
        }

