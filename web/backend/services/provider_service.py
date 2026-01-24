"""Provider service for managing LLM providers and API key validation."""
from typing import Optional, Dict, List, Any
import os
import logging
from ..models import ProviderEnum, ProviderInfo, ValidateKeyResponse

logger = logging.getLogger(__name__)


class ProviderService:
    """Service for managing LLM providers."""
    
    # Provider metadata
    PROVIDER_METADATA: Dict[ProviderEnum, Dict[str, Any]] = {
        ProviderEnum.MOCK: {
            "name": "Mock Provider",
            "requires_api_key": False,
            "supported_models": ["mock-model", "mock-advanced"],
            "api_key_env_var": None,
        },
        ProviderEnum.OLLAMA: {
            "name": "Ollama (Local)",
            "requires_api_key": False,
            "supported_models": ["llama3.2", "mistral", "codellama", "phi3"],
            "api_key_env_var": None,
        },
        ProviderEnum.OPENAI: {
            "name": "OpenAI",
            "requires_api_key": True,
            "supported_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "api_key_env_var": "OPENAI_API_KEY",
        },
        ProviderEnum.ANTHROPIC: {
            "name": "Anthropic Claude",
            "requires_api_key": True,
            "supported_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "api_key_env_var": "ANTHROPIC_API_KEY",
        },
        ProviderEnum.GOOGLE: {
            "name": "Google Gemini",
            "requires_api_key": True,
            "supported_models": ["gemini-pro", "gemini-pro-vision"],
            "api_key_env_var": "GOOGLE_API_KEY",
        },
        ProviderEnum.AZURE_OPENAI: {
            "name": "Azure OpenAI",
            "requires_api_key": True,
            "supported_models": ["gpt-4", "gpt-35-turbo"],
            "api_key_env_var": "AZURE_OPENAI_API_KEY",
        },
    }
    
    def list_providers(self, include_models: bool = False) -> list[ProviderInfo]:
        """Get list of available providers.
        
        Args:
            include_models: Whether to include model lists in response
            
        Returns:
            List of ProviderInfo objects
        """
        providers = []
        for provider_id, metadata in self.PROVIDER_METADATA.items():
            providers.append(ProviderInfo(
                id=provider_id.value,
                name=metadata["name"],
                requires_api_key=metadata["requires_api_key"],
                supported_models=metadata["supported_models"] if include_models else [],
                api_key_env_var=metadata["api_key_env_var"],
            ))
        return providers
    
    def get_provider_info(self, provider: ProviderEnum) -> Optional[ProviderInfo]:
        """Get information about a specific provider.
        
        Args:
            provider: Provider to get info for
            
        Returns:
            ProviderInfo or None if not found
        """
        metadata = self.PROVIDER_METADATA.get(provider)
        if not metadata:
            return None
            
        return ProviderInfo(
            id=provider.value,
            name=metadata["name"],
            requires_api_key=metadata["requires_api_key"],
            supported_models=metadata["supported_models"],
            api_key_env_var=metadata["api_key_env_var"],
        )
    
    def get_api_key(self, provider: ProviderEnum, override_key: Optional[str] = None) -> Optional[str]:
        """Get API key for provider (from override or environment).
        
        Args:
            provider: Provider to get key for
            override_key: Optional key provided by user (takes precedence)
            
        Returns:
            API key or None if not available
        """
        # Check override first
        if override_key:
            return override_key
            
        # Check environment variable
        metadata = self.PROVIDER_METADATA.get(provider)
        if metadata and metadata["api_key_env_var"]:
            return os.getenv(metadata["api_key_env_var"])
            
        return None
    
    async def validate_api_key(
        self,
        provider: ProviderEnum,
        api_key: str,
        model: Optional[str] = None
    ) -> ValidateKeyResponse:
        """Validate an API key for a provider.
        
        Args:
            provider: Provider to validate against
            api_key: API key to validate
            model: Optional specific model to test
            
        Returns:
            ValidateKeyResponse with validation result
        """
        # Mock and Ollama don't need keys
        if provider in [ProviderEnum.MOCK, ProviderEnum.OLLAMA]:
            return ValidateKeyResponse(
                valid=True,
                message="No API key required for this provider",
                models_available=None,
            )
        
        # For real providers, we'll implement actual validation in phase 2
        # For now, just check key format
        if not api_key or len(api_key) < 10:
            return ValidateKeyResponse(
                valid=False,
                message="API key is too short or empty",
                models_available=None,
            )
        
        # TODO: Implement actual provider-specific validation
        # This would involve making a test API call to the provider
        provider_info = self.get_provider_info(provider)
        
        return ValidateKeyResponse(
            valid=True,
            message=f"API key format valid for {provider.value}",
            models_available=provider_info.supported_models if provider_info else None,
        )
