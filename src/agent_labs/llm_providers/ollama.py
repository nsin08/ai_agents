"""
Ollama LLM provider for local model inference.

OllamaProvider integrates with Ollama (https://ollama.ai) - a tool to run
large language models locally. Perfect for:
- Local development (no API costs)
- Privacy-sensitive use cases (data stays local)
- On-device inference (GPU/CPU optimized)
- Testing with real LLMs

Setup:
1. Install Ollama: https://ollama.ai
2. Pull a model: ollama pull llama2
3. Start server: ollama serve
4. Create provider: OllamaProvider(base_url="http://localhost:11434")

Models available:
- llama2 (Meta's Llama 2, 7B-70B)
- mistral (Mistral 7B)
- neural-chat (Intel Neural Chat)
- And others: https://ollama.ai/library
"""

import asyncio
from typing import AsyncIterator, Optional

from .base import Provider, LLMResponse
from .exceptions import (
    ProviderConnectionError,
    ProviderTimeoutError,
    ModelNotFoundError,
    ProviderConfigError,
)


class OllamaProvider(Provider):
    """
    Local Ollama LLM provider.
    
    Connects to Ollama running locally via HTTP API.
    Requires: ollama serve running (default: http://localhost:11434)
    
    Example:
        >>> provider = OllamaProvider(model="llama2")
        >>> response = await provider.generate("What is Python?")
        >>> print(response.text)
        >>> print(response.tokens_used)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        timeout: int = 60,
    ):
        """
        Initialize OllamaProvider.
        
        Args:
            base_url: Ollama server URL (default: localhost:11434)
            model: Model name to use (default: llama2)
            timeout: Request timeout in seconds (default: 60)
            
        Raises:
            ProviderConfigError: If configuration is invalid
        """
        if not base_url:
            raise ProviderConfigError("base_url cannot be empty")
        if not model:
            raise ProviderConfigError("model cannot be empty")
        if timeout <= 0:
            raise ProviderConfigError("timeout must be positive")
        
        self.base_url = base_url.rstrip("/")  # Remove trailing slash
        self.model = model
        self.timeout = timeout
        self._client = None
        
    async def _ensure_client(self):
        """Lazy load httpx client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(timeout=self.timeout)
            except ImportError:
                raise ProviderConfigError(
                    "httpx is required for OllamaProvider. "
                    "Install with: pip install httpx"
                )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            LLMResponse with generated text
            
        Raises:
            ProviderConnectionError: If cannot connect to Ollama
            ProviderTimeoutError: If request times out
            ModelNotFoundError: If model is not available
        """
        await self._ensure_client()
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        try:
            response = await self._client.post(url, json=payload)
            
            if response.status_code == 404:
                raise ModelNotFoundError(
                    f"Model '{self.model}' not found in Ollama. "
                    f"Available models: Run 'ollama list'"
                )
            
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data.get("response", ""),
                tokens_used=data.get("eval_count", 0),
                model=self.model
            )
            
        except asyncio.TimeoutError as e:
            raise ProviderTimeoutError(
                f"Ollama request timed out after {self.timeout}s"
            ) from e
        except ConnectionError as e:
            raise ProviderConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            ) from e

    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """
        Stream text generation from Ollama.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Yields:
            Text chunks as they arrive
            
        Raises:
            ProviderConnectionError: If cannot connect to Ollama
            ProviderTimeoutError: If request times out
            ModelNotFoundError: If model is not available
        """
        await self._ensure_client()
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
            }
        }
        
        try:
            async with self._client.stream("POST", url, json=payload) as response:
                if response.status_code == 404:
                    raise ModelNotFoundError(
                        f"Model '{self.model}' not found in Ollama"
                    )
                
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token
                            
        except asyncio.TimeoutError as e:
            raise ProviderTimeoutError(
                f"Ollama streaming timed out after {self.timeout}s"
            ) from e
        except ConnectionError as e:
            raise ProviderConnectionError(
                f"Cannot connect to Ollama at {self.base_url}"
            ) from e

    async def count_tokens(self, text: str) -> int:
        """
        Estimate token count.
        
        Note: Ollama doesn't provide token counting API,
        so we use a simple heuristic (1 token per word).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        # Simple heuristic: ~1 token per word
        return len(text.split())

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
