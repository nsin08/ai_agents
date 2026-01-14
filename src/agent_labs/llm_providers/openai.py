"""OpenAI LLM Provider implementation.

Supports OpenAI API (GPT-4, GPT-3.5, etc.) with proper error handling and retries.
"""

import os
import time
from typing import AsyncIterator, Optional

from .base import Provider, LLMResponse
from .exceptions import (
    ProviderAuthError,
    ProviderConnectionError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    TokenLimitExceededError,
    ModelNotFoundError,
)


class OpenAIProvider(Provider):
    """OpenAI API provider for GPT models.
    
    Supports all OpenAI chat models (GPT-4, GPT-3.5-turbo, etc.).
    Requires OPENAI_API_KEY environment variable.
    
    Args:
        api_key: OpenAI API key (if not provided, reads from OPENAI_API_KEY env var)
        model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
        base_url: API base URL (default: https://api.openai.com/v1)
        timeout: Request timeout in seconds
        temperature: Sampling temperature (0.0-2.0)
        max_retries: Maximum retry attempts for rate limits
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 30,
        temperature: float = 0.7,
        max_retries: int = 3,
    ):
        """Initialize OpenAI provider."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ProviderAuthError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable."
            )
        
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.default_timeout = timeout
        self.default_temperature = temperature
        self.max_retries = max_retries
        
        # Lazy import to avoid dependency if not using OpenAI
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.default_timeout,
            )
        except ImportError:
            raise ProviderAuthError(
                "OpenAI package not installed. Install with: pip install openai"
            )
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate response from OpenAI API.
        
        Args:
            prompt: Input prompt/query
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
        
        Returns:
            LLMResponse with generated text and token count
            
        Raises:
            ProviderAuthError: Invalid API key
            ProviderRateLimitError: Rate limit exceeded
            ProviderTimeoutError: Request timeout
            ProviderConnectionError: Network/connection issues
            TokenLimitExceededError: Input too long
            ModelNotFoundError: Invalid model name
        """
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ]
        
        # Retry logic for rate limits
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                
                # Extract response
                content = response.choices[0].message.content
                tokens = response.usage.total_tokens
                
                return LLMResponse(
                    text=content,
                    tokens_used=tokens,
                    model=self.model,
                )
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Authentication error
                if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                    raise ProviderAuthError(f"OpenAI authentication failed: {e}")
                
                # Rate limit - retry with backoff
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    raise ProviderRateLimitError(f"OpenAI rate limit exceeded after {self.max_retries} retries")
                
                # Timeout
                if "timeout" in error_msg or "timed out" in error_msg:
                    raise ProviderTimeoutError(f"OpenAI request timeout after {self.default_timeout}s")
                
                # Token limit
                if "maximum context length" in error_msg or "token limit" in error_msg:
                    raise TokenLimitExceededError(f"OpenAI token limit exceeded: {e}")
                
                # Model not found
                if "model" in error_msg and ("not found" in error_msg or "does not exist" in error_msg):
                    raise ModelNotFoundError(f"OpenAI model '{self.model}' not found: {e}")
                
                # Connection/network error
                if "connection" in error_msg or "network" in error_msg:
                    raise ProviderConnectionError(f"OpenAI connection error: {e}")
                
                # Generic error
                raise ProviderConnectionError(f"OpenAI API error: {e}")
        
        # Should not reach here
        raise ProviderRateLimitError(f"OpenAI rate limit exceeded after {self.max_retries} retries")
    
    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """Stream text response tokens as they arrive.
        
        Args:
            prompt: Input text
            max_tokens: Maximum tokens to generate
            
        Yields:
            Chunks of generated text
        """
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                raise ProviderAuthError(f"OpenAI authentication failed: {e}")
            raise ProviderConnectionError(f"OpenAI streaming error: {e}")
    
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Uses tiktoken library for accurate token counting.
        
        Args:
            text: Text to count
            
        Returns:
            Number of tokens
        """
        try:
            import tiktoken
            
            # Get encoding for model
            if "gpt-4" in self.model:
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif "gpt-3.5" in self.model:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                # Default to cl100k_base (GPT-4/3.5 encoding)
                encoding = tiktoken.get_encoding("cl100k_base")
            
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: rough approximation (4 chars = 1 token)
            return len(text) // 4
    
    def __repr__(self) -> str:
        """String representation."""
        return f"OpenAIProvider(model={self.model}, base_url={self.base_url})"
