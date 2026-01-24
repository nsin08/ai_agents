"""Factory for creating LLM provider instances."""
from typing import Optional
import os
import sys
from pathlib import Path

# Add src to path to import agent_labs
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_labs.llm_providers import (
    Provider,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
    CloudProvider,
    ProviderConfigError,
)
from agent_labs.config import ProviderConfig
from models import ProviderEnum


class ProviderFactory:
    """Factory for creating configured provider instances."""
    
    @staticmethod
    def create_provider(
        provider_type: ProviderEnum,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Provider:
        """Create a provider instance.
        
        Args:
            provider_type: Type of provider to create
            model: Model name to use
            api_key: Optional API key (overrides env var)
            base_url: Optional base URL for API
            
        Returns:
            Configured Provider instance
            
        Raises:
            ProviderConfigError: If provider configuration is invalid
        """
        # Mock provider
        if provider_type == ProviderEnum.MOCK:
            return MockProvider(name=model)
        
        # Ollama provider (local)
        if provider_type == ProviderEnum.OLLAMA:
            return OllamaProvider(
                model=model,
                base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
        
        # OpenAI provider
        if provider_type == ProviderEnum.OPENAI:
            api_key_resolved = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key_resolved:
                raise ProviderConfigError("OpenAI API key required but not provided")
            
            return OpenAIProvider(
                api_key=api_key_resolved,
                model=model,
                base_url=base_url,
            )
        
        # Anthropic provider
        if provider_type == ProviderEnum.ANTHROPIC:
            api_key_resolved = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key_resolved:
                raise ProviderConfigError("Anthropic API key required but not provided")
            
            return CloudProvider(
                provider_name="anthropic",
                api_key=api_key_resolved,
                model=model,
                base_url=base_url or "https://api.anthropic.com",
            )
        
        # Google provider
        if provider_type == ProviderEnum.GOOGLE:
            api_key_resolved = api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key_resolved:
                raise ProviderConfigError("Google API key required but not provided")
            
            return CloudProvider(
                provider_name="google",
                api_key=api_key_resolved,
                model=model,
                base_url=base_url or "https://generativelanguage.googleapis.com",
            )
        
        # Azure OpenAI provider
        if provider_type == ProviderEnum.AZURE_OPENAI:
            api_key_resolved = api_key or os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key_resolved:
                raise ProviderConfigError("Azure OpenAI API key required but not provided")
            
            # Azure requires endpoint from env var or base_url
            endpoint = base_url or os.getenv("AZURE_OPENAI_ENDPOINT")
            if not endpoint:
                raise ProviderConfigError("Azure OpenAI endpoint required but not provided")
            
            return CloudProvider(
                provider_name="azure-openai",
                api_key=api_key_resolved,
                model=model,
                base_url=endpoint,
            )
        
        raise ProviderConfigError(f"Unknown provider type: {provider_type}")
