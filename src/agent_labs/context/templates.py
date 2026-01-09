"""
Prompt template utilities and summarization helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional

from ..llm_providers import Provider, MockProvider


class TemplateEngine(str, Enum):
    """Template rendering engines."""

    SIMPLE = "simple"
    JINJA2 = "jinja2"


@dataclass
class PromptTemplate:
    """Prompt template with variable substitution."""

    template: str
    variables: List[str] = field(default_factory=list)
    engine: TemplateEngine = TemplateEngine.SIMPLE

    def __post_init__(self) -> None:
        self._validate_template_variables()

    def format(self, **kwargs: str) -> str:
        """Render the prompt template with provided variables."""
        self._validate_variables(kwargs)
        if self.engine == TemplateEngine.SIMPLE:
            return self.template.format(**kwargs)
        return self._render_jinja(kwargs)

    def _validate_template_variables(self) -> None:
        import re
        if self.engine == TemplateEngine.SIMPLE:
            found = set(re.findall(r"\{(\w+)\}", self.template))
        else:
            found = set(re.findall(r"\{\{\s*(\w+)", self.template))
        declared = set(self.variables)
        missing = found - declared
        if missing:
            raise ValueError(f"Variables in template not declared: {', '.join(sorted(missing))}")

    def _validate_variables(self, values: Dict[str, str]) -> None:
        missing = [var for var in self.variables if var not in values]
        if missing:
            raise ValueError(f"Missing variables: {', '.join(missing)}")

    def _render_jinja(self, values: Dict[str, str]) -> str:
        try:
            import jinja2
        except ImportError as exc:
            raise ImportError("Jinja2 required for JINJA2 engine") from exc
        env = jinja2.Environment(autoescape=False)
        template = env.from_string(self.template)
        return template.render(**values)

    def get_token_count(self, **kwargs: str) -> int:
        from .tokens import TokenCounter
        rendered = self.format(**kwargs)
        return TokenCounter.count(rendered)


async def summarize_with_provider(
    provider: Provider,
    text: str,
    max_tokens: int = 150,
    temperature: float = 0.3,
) -> str:
    """Summarize text using an LLM provider."""
    prompt = (
        "Summarize the following text in concise bullet points.\n\n"
        f"Text:\n{text}\n\nSummary:"
    )
    response = await provider.generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.text


class ContextSummarizer:
    """Summarize text with deterministic mock fallback."""

    def __init__(
        self,
        provider: Optional[Provider] = None,
        max_input_chars: int = 10000,
    ) -> None:
        self.provider = provider or MockProvider()
        self.max_input_chars = max_input_chars

    async def summarize(self, text: str, max_length: int = 500) -> str:
        if len(text) > self.max_input_chars:
            text = text[: self.max_input_chars]

        if isinstance(self.provider, MockProvider):
            sentences = [s.strip() for s in text.split(".") if s.strip()]
            if not sentences:
                return text.strip()
            kept = sentences[: max(1, len(sentences) // 3)]
            summary = ". ".join(kept).strip()
            words = summary.split()
            if len(words) > max_length:
                summary = " ".join(words[:max_length])
            return summary

        response = await self.provider.generate(
            f"Summarize in {max_length} words:\n{text}",
            max_tokens=max_length,
        )
        return response.text
