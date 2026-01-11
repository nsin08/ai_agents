"""
Context Engineering Agent

This module implements sophisticated prompt and context management for agents.
It provides:
- Token counting and context window management
- Prompt template rendering with variable substitution
- Context overflow prevention through chunking and truncation
- Few-shot learning example integration

Key Concepts:
1. Token Budget: Calculate available tokens for system prompt, context, and response
2. Context Overflow: Prevent exceeding model's context window
3. Template Rendering: Safely fill templates with variables
4. Chunking Strategy: Split large documents to fit token constraints
5. Few-Shot Learning: Use in-context examples to guide behavior
"""

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class TokenBudget:
    """Tracks token usage across prompt components."""
    system_prompt: int
    context: int
    response: int
    
    @property
    def total(self) -> int:
        """Total tokens reserved."""
        return self.system_prompt + self.context + self.response
    
    def available_for_context(self, max_tokens: int) -> int:
        """Calculate available tokens for context after reservations."""
        return max(0, max_tokens - self.system_prompt - self.response - 500)  # 500 token buffer


class ContextAgent:
    """
    Agent for managing prompts and context windows.
    
    Handles:
    - Token counting (simulated without external dependencies)
    - Template rendering with variable substitution
    - Context window overflow prevention
    - Text chunking and truncation
    - Few-shot example management
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 8000):
        """
        Initialize context agent.
        
        Args:
            model: LLM model name (used for token estimation)
            max_tokens: Context window size for target model
        """
        self.model = model
        self.max_tokens = max_tokens
        self.templates = {}
        self.examples = {}
        
        # Simple token estimation: ~4 chars per token (tiktoken approximation)
        self._chars_per_token = 4
    
    def register_template(self, name: str, template: str) -> None:
        """
        Register a prompt template for later use.
        
        Args:
            name: Template identifier
            template: Template string with {variable} placeholders
        
        Raises:
            ValueError: If template name already exists
        """
        if name in self.templates:
            raise ValueError(f"Template '{name}' already registered")
        self.templates[name] = template
    
    def register_examples(self, category: str, examples: list[dict]) -> None:
        """
        Register few-shot learning examples for a task category.
        
        Args:
            category: Example category (e.g., 'sentiment_analysis')
            examples: List of example dicts with required fields
        """
        self.examples[category] = examples
    
    def render_template(self, name: str, **kwargs) -> str:
        """
        Fill template with provided variables.
        
        Args:
            name: Template name
            **kwargs: Variables to substitute in template
        
        Returns:
            Rendered template string
        
        Raises:
            ValueError: If template not found or variable missing
        """
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        
        template = self.templates[name]
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count in text.
        
        Uses simple approximation: ~4 characters per token.
        For production, use tiktoken or model's tokenizer.
        
        Args:
            text: Text to count
        
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return max(1, len(text) // self._chars_per_token)
    
    def truncate_to_fit(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token budget.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
        
        Returns:
            Truncated text (may be empty if max_tokens is 0)
        """
        tokens = self.count_tokens(text)
        
        if tokens <= max_tokens:
            return text
        
        # Calculate approximate character limit
        char_limit = max_tokens * self._chars_per_token
        return text[:char_limit]
    
    def chunk_text(self, text: str, chunk_size: int) -> list[str]:
        """
        Split text into token-sized chunks.
        
        Chunks are approximated by character count to match token size.
        
        Args:
            text: Text to chunk
            chunk_size: Target tokens per chunk
        
        Returns:
            List of text chunks
        
        Raises:
            ValueError: If chunk_size is 0 or negative
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        # Convert chunk size from tokens to approximate characters
        chars_per_chunk = chunk_size * self._chars_per_token
        
        chunks = []
        for i in range(0, len(text), chars_per_chunk):
            chunk = text[i:i + chars_per_chunk]
            if chunk.strip():  # Only include non-empty chunks
                chunks.append(chunk)
        
        return chunks if chunks else [text]  # Return original if all empty
    
    def render_with_context_check(self, name: str, **kwargs) -> str:
        """
        Render template and verify token budget.
        
        Args:
            name: Template name
            **kwargs: Variables to substitute
        
        Returns:
            Rendered template
        
        Raises:
            ValueError: If rendered prompt exceeds context window
        """
        rendered = self.render_template(name, **kwargs)
        token_count = self.count_tokens(rendered)
        
        if token_count > self.max_tokens:
            raise ValueError(
                f"Prompt exceeds token limit: {token_count}/{self.max_tokens} tokens"
            )
        
        return rendered
    
    def manage_context(
        self,
        document: str,
        max_tokens: Optional[int] = None,
        strategy: str = "truncate"
    ) -> Union[str, list[str]]:
        """
        Manage context for large documents.
        
        Prevents token overflow using specified strategy:
        - 'truncate': Cut document to fit token limit
        - 'chunk': Split document into smaller pieces
        
        Args:
            document: Input document
            max_tokens: Token limit (uses instance max_tokens if not provided)
            strategy: Management strategy ('truncate' or 'chunk')
        
        Returns:
            Managed document (string for truncate, list for chunk)
        
        Raises:
            ValueError: If strategy is invalid
        """
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        if strategy not in ("truncate", "chunk"):
            raise ValueError(f"Unknown strategy: {strategy}")
        
        doc_tokens = self.count_tokens(document)
        
        # Reserve tokens for system prompt and response
        available = max_tokens - 500  # 500 token buffer
        
        if doc_tokens <= available:
            return document
        
        if strategy == "truncate":
            return self.truncate_to_fit(document, available)
        else:  # chunk
            # Use at least 100 token chunks to avoid 0 chunk size
            chunk_size = max(100, available // 3)
            return self.chunk_text(document, chunk_size)
    
    def get_budget_summary(
        self,
        prompt: str,
        system_prompt_tokens: int = 200,
        response_tokens: int = 500
    ) -> dict:
        """
        Get token budget summary for a prompt.
        
        Args:
            prompt: Prompt text
            system_prompt_tokens: Tokens reserved for system prompt
            response_tokens: Tokens reserved for response
        
        Returns:
            Dict with budget breakdown and availability
        """
        prompt_tokens = self.count_tokens(prompt)
        
        budget = TokenBudget(
            system_prompt=system_prompt_tokens,
            context=prompt_tokens,
            response=response_tokens
        )
        
        available = self.max_tokens - budget.total
        overflow = max(0, budget.total - self.max_tokens)
        
        return {
            "model": self.model,
            "context_window": self.max_tokens,
            "system_prompt": system_prompt_tokens,
            "prompt": prompt_tokens,
            "response": response_tokens,
            "total_used": budget.total,
            "available": available,
            "overflow": overflow,
            "fits": available >= 0
        }
    
    def get_template_names(self) -> list[str]:
        """Get list of registered template names."""
        return list(self.templates.keys())
    
    def get_example_categories(self) -> list[str]:
        """Get list of registered example categories."""
        return list(self.examples.keys())
    
    def format_examples(self, category: str, format_str: str = "{text}") -> str:
        """
        Format examples for inclusion in prompts.
        
        Args:
            category: Example category
            format_str: How to format each example (e.g., "Text: {text}")
        
        Returns:
            Formatted examples as newline-separated string
        
        Raises:
            ValueError: If category not found
        """
        if category not in self.examples:
            raise ValueError(f"Example category '{category}' not found")
        
        examples = self.examples[category]
        formatted = []
        
        for example in examples:
            try:
                formatted.append(format_str.format(**example))
            except KeyError as e:
                raise ValueError(f"Missing field in example: {e}")
        
        return "\n".join(formatted)
