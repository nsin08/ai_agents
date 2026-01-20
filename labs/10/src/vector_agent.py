"""Vector retrieval + context packing + memory consolidation (educational)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.agent_labs.context import ContextManifest, TokenCounter
from src.agent_labs.retrieval import RetrievedChunk, VectorIndex


@dataclass
class Episode:
    tenant_id: str
    question: str
    answer: str
    citations: list[dict]


@dataclass
class SemanticFact:
    key: str
    value: str
    tenant_id: str


@dataclass
class VectorRagAgent:
    index: VectorIndex
    max_tokens: int = 2000
    reserved_response_tokens: int = 200
    episodes: List[Episode] = field(default_factory=list)
    semantic_facts: Dict[str, SemanticFact] = field(default_factory=dict)

    def answer(
        self,
        question: str,
        *,
        tenant_id: str,
        request_id: str,
        top_k: int = 2,
    ) -> dict:
        retrieved = self.index.query(
            question,
            top_k=top_k,
            filters={"tenant_id": tenant_id},
        )

        manifest = ContextManifest(
            request_id=request_id,
            max_tokens=self.max_tokens,
            reserved_response_tokens=self.reserved_response_tokens,
        )

        citations: list[dict] = []
        for chunk in retrieved:
            citations.append(
                {
                    "doc_id": chunk.doc_id,
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.metadata.get("source"),
                }
            )
            manifest.add_item(
                kind="evidence",
                tokens=TokenCounter.count(chunk.text),
                reason="retrieval_top_k",
                metadata={
                    "doc_id": chunk.doc_id,
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.metadata.get("source"),
                },
            )

        answer_text = self._generate_deterministic_answer(question, retrieved)

        self.episodes.append(
            Episode(
                tenant_id=tenant_id,
                question=question,
                answer=answer_text,
                citations=citations,
            )
        )
        self._consolidate_memory(tenant_id=tenant_id)

        return {
            "answer": answer_text,
            "citations": citations,
            "manifest": manifest.to_dict(),
        }

    @staticmethod
    def _generate_deterministic_answer(question: str, retrieved: List[RetrievedChunk]) -> str:
        # Deterministic generation for offline evaluation.
        q = question.lower()
        if "mcp" in q:
            return "MCP is a tool server protocol."
        if "reset password" in q or "reset" in q:
            return "Reset password steps."
        if retrieved:
            # Fallback: use the first few words of top chunk.
            return " ".join(retrieved[0].text.split()[:4]).strip() or "No answer."
        return "No answer."

    def _consolidate_memory(self, *, tenant_id: str) -> None:
        # Simple, deterministic consolidation: store last answer per tenant.
        if not self.episodes:
            return
        last = self.episodes[-1]
        key = f"{tenant_id}:last_answer"
        self.semantic_facts[key] = SemanticFact(
            key=key,
            value=last.answer,
            tenant_id=tenant_id,
        )

