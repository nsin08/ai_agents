from __future__ import annotations

from _bootstrap import add_repo_src_to_path

add_repo_src_to_path()

from agent_labs.context import PromptTemplate
from agent_labs.context.tokens import TokenCounter


def main() -> None:
    template = PromptTemplate(
        template="Summarize: {text}\n\nConstraints: {constraints}",
        variables=["text", "constraints"],
    )
    rendered = template.format(
        text="This is a long message that we want to keep within a budget.",
        constraints="Be concise. Use bullet points.",
    )
    estimated = TokenCounter.count(rendered)

    print("OK: rendered_len=", len(rendered))
    print("OK: estimated_tokens=", estimated)
    print("OK: fits_128=", TokenCounter.fits(rendered, max_tokens=128))


if __name__ == "__main__":
    main()

