"""
Common prompt templates for context engineering.
"""

from .templates import PromptTemplate


QA_TEMPLATE = PromptTemplate(
    template=(
        "You are a helpful assistant.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
    variables=["context", "question"],
)


REASONING_TEMPLATE = PromptTemplate(
    template=(
        "You are a reasoning assistant.\n\n"
        "Context:\n{context}\n\n"
        "Task: {task}\n\n"
        "Provide a step-by-step answer:"
    ),
    variables=["context", "task"],
)


TOOL_USE_TEMPLATE = PromptTemplate(
    template=(
        "You can use tools.\n\n"
        "Available tools:\n{tools}\n\n"
        "User request: {request}\n\n"
        "Plan:"
    ),
    variables=["tools", "request"],
)
