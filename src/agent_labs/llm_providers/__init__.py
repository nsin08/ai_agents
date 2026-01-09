"""LLM Provider abstraction layer.

Exports:
- Provider: Abstract base class for all providers
- LLMResponse: Response dataclass
- MockProvider: Deterministic testing provider
- OllamaProvider: Local model inference provider
- Custom exceptions: Error handling for different failure modes
"""

from .base import Provider, LLMResponse
from .mock import MockProvider
from .ollama import OllamaProvider
from .exceptions import (
    ProviderError,
    ProviderConnectionError,
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderAuthError,
    ProviderConfigError,
    ModelNotFoundError,
    TokenLimitExceededError,
)

__all__ = [
    # Core classes
    "Provider",
    "LLMResponse",
    # Implementations
    "MockProvider",
    "OllamaProvider",
    # Exceptions
    "ProviderError",
    "ProviderConnectionError",
    "ProviderTimeoutError",
    "ProviderRateLimitError",
    "ProviderAuthError",
    "ProviderConfigError",
    "ModelNotFoundError",
    "TokenLimitExceededError",
]
