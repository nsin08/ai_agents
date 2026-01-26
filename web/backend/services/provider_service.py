"""Provider service for managing LLM providers and API key validation."""
from typing import Optional, Dict, List, Any
import os
import sys
import logging
import httpx
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ProviderEnum, ProviderInfo, ValidateKeyResponse

logger = logging.getLogger(__name__)


class ProviderService:
    """Service for managing LLM providers."""
    
    def __init__(self):
        """Initialize provider service."""
        self._ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    async def _fetch_ollama_models(self) -> List[str]:
        """Fetch available models from Ollama API.
        
        Returns:
            List of model names from running Ollama instance
        """
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self._ollama_base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    # Extract model names (format: "name:tag" or just "name")
                    model_names = []
                    for model in models:
                        name = model.get("name", "")
                        if name:
                            # Remove ":latest" suffix for cleaner display
                            if name.endswith(":latest"):
                                name = name[:-7]
                            model_names.append(name)
                    if model_names:
                        logger.info(f"Fetched {len(model_names)} models from Ollama: {model_names}")
                        return model_names
        except Exception as e:
            logger.warning(f"Could not fetch Ollama models: {e}")
        
        # Fallback to env var or default
        return self._get_models_from_env("OLLAMA_MODELS", ["llama3.2", "mistral", "codellama", "phi3"])
    
    @staticmethod
    def _get_models_from_env(env_var: str, default: List[str]) -> List[str]:
        """Get model list from environment variable or use default.
        
        Args:
            env_var: Environment variable name (e.g., "OPENAI_MODELS")
            default: Default models if env var not set
            
        Returns:
            List of model names
        """
        env_value = os.getenv(env_var)
        if env_value:
            # Support comma-separated list
            return [m.strip() for m in env_value.split(",") if m.strip()]
        return default
    
    # Provider metadata
    PROVIDER_METADATA: Dict[ProviderEnum, Dict[str, Any]] = {
        ProviderEnum.MOCK: {
            "name": "Mock Provider",
            "requires_api_key": False,
            "supported_models": None,  # Will be populated dynamically
            "api_key_env_var": None,
            "status": "available",  # fully implemented
        },
        ProviderEnum.OLLAMA: {
            "name": "Ollama (Local)",
            "requires_api_key": False,
            "supported_models": None,  # Will be fetched from Ollama API
            "api_key_env_var": None,
            "status": "available",  # fully implemented
        },
        ProviderEnum.OPENAI: {
            "name": "OpenAI",
            "requires_api_key": True,
            "supported_models": None,  # Will be populated dynamically
            "api_key_env_var": "OPENAI_API_KEY",
            "status": "available",  # fully implemented
        },
        ProviderEnum.ANTHROPIC: {
            "name": "Anthropic Claude",
            "requires_api_key": True,
            "supported_models": None,  # Will be populated dynamically
            "api_key_env_var": "ANTHROPIC_API_KEY",
            "status": "coming_soon",  # TODO: implement AnthropicProvider
        },
        ProviderEnum.GOOGLE: {
            "name": "Google Gemini",
            "requires_api_key": True,
            "supported_models": None,  # Will be populated dynamically
            "api_key_env_var": "GOOGLE_API_KEY",
            "status": "coming_soon",  # TODO: implement GoogleProvider
        },
        ProviderEnum.AZURE_OPENAI: {
            "name": "Azure OpenAI",
            "requires_api_key": True,
            "supported_models": None,  # Will be populated dynamically
            "api_key_env_var": "AZURE_OPENAI_API_KEY",
            "status": "coming_soon",  # TODO: implement AzureOpenAIProvider
        },
    }
    
    async def _get_provider_models(self, provider: ProviderEnum) -> List[str]:
        """Get models for a specific provider dynamically.
        
        Args:
            provider: Provider to get models for
            
        Returns:
            List of model names
        """
        if provider == ProviderEnum.OLLAMA:
            return await self._fetch_ollama_models()
        elif provider == ProviderEnum.MOCK:
            return self._get_models_from_env("MOCK_MODELS", ["mock-model", "mock-advanced"])
        elif provider == ProviderEnum.OPENAI:
            return self._get_models_from_env("OPENAI_MODELS", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        elif provider == ProviderEnum.ANTHROPIC:
            return self._get_models_from_env("ANTHROPIC_MODELS", ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"])
        elif provider == ProviderEnum.GOOGLE:
            return self._get_models_from_env("GOOGLE_MODELS", ["gemini-pro", "gemini-pro-vision"])
        elif provider == ProviderEnum.AZURE_OPENAI:
            return self._get_models_from_env("AZURE_OPENAI_MODELS", ["gpt-4", "gpt-35-turbo"])
        else:
            return []
    
    async def list_providers(self, include_models: bool = False) -> list[ProviderInfo]:
        """Get list of available providers.
        
        Args:
            include_models: Whether to include model lists in response
            
        Returns:
            List of ProviderInfo objects
        """
        providers = []
        for provider_id, metadata in self.PROVIDER_METADATA.items():
            models = []
            if include_models:
                models = await self._get_provider_models(provider_id)
            
            providers.append(ProviderInfo(
                id=provider_id.value,
                name=metadata["name"],
                requires_api_key=metadata["requires_api_key"],
                supported_models=models,
                api_key_env_var=metadata["api_key_env_var"],
                status=metadata.get("status", "available"),
            ))
        return providers
    
    async def get_provider_info(self, provider: ProviderEnum) -> Optional[ProviderInfo]:
        """Get information about a specific provider.
        
        Args:
            provider: Provider to get info for
            
        Returns:
            ProviderInfo or None if not found
        """
        metadata = self.PROVIDER_METADATA.get(provider)
        if not metadata:
            return None
        
        models = await self._get_provider_models(provider)
            
        return ProviderInfo(
            id=provider.value,
            name=metadata["name"],
            requires_api_key=metadata["requires_api_key"],
            supported_models=models,
            api_key_env_var=metadata["api_key_env_var"],
            status=metadata.get("status", "available"),
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
        provider_info = await self.get_provider_info(provider)
        
        return ValidateKeyResponse(
            valid=True,
            message=f"API key format valid for {provider.value}",
            models_available=provider_info.supported_models if provider_info else None,
        )
