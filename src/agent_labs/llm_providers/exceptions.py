"""
Custom exceptions for LLM Provider module.

Defines specific exceptions for different failure modes when interacting with LLM providers.
"""


class ProviderError(Exception):
    """Base exception for all provider-related errors."""
    
    pass


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to the provider (network error)."""
    
    pass


class ProviderTimeoutError(ProviderError):
    """Raised when a provider request times out."""
    
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = 60):
        """
        Initialize rate limit error.
        
        Args:
            message: Error description
            retry_after: Seconds to wait before retrying (default: 60)
        """
        super().__init__(message)
        self.retry_after = retry_after


class ProviderAuthError(ProviderError):
    """Raised when authentication fails (invalid API key, etc.)."""
    
    pass


class ProviderConfigError(ProviderError):
    """Raised when provider configuration is invalid."""
    
    pass


class ModelNotFoundError(ProviderError):
    """Raised when the specified model is not available."""
    
    pass


class TokenLimitExceededError(ProviderError):
    """Raised when request exceeds token limits."""
    
    pass
