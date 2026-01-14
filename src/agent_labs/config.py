"""
Configuration management for agent_labs.

Provides centralized configuration for LLM models, providers, and tool settings.
Supports multiple providers: Mock, Ollama, OpenAI, Anthropic, Google, Azure OpenAI.
"""

import os
from typing import Optional, Tuple, Dict, Any
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure-openai"


class OllamaModel(str, Enum):
    """Available Ollama models."""
    MISTRAL = "mistral:7b"
    LLAMA2 = "llama2"
    LLAMA2_13B = "llama2:13b"
    NEURAL_CHAT = "neural-chat"
    QWEN = "qwen"
    GEMMA = "gemma"

    @classmethod
    def from_string(cls, value: str) -> "OllamaModel":
        """Convert string to OllamaModel, with fallback to custom model name."""
        try:
            return cls[value.upper().replace(":", "_").replace(".", "_")]
        except KeyError:
            # Allow custom model names
            return value


class ProviderConfig:
    """Provider-specific configuration with authentication support."""
    
    def __init__(self, provider: LLMProvider):
        """
        Initialize provider configuration.
        
        Args:
            provider: LLM provider type
        """
        self.provider = provider
        self.model = self._get_model()
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.timeout = self._get_timeout()
        self.temperature = self._get_temperature()
    
    def _get_model(self) -> Optional[str]:
        """Get model name from environment with provider-specific defaults."""
        # Try provider-specific env var first
        env_key = f"{self.provider.value.upper().replace('-', '_')}_MODEL"
        model = os.getenv(env_key)
        
        if model:
            return model
        
        # Fall back to LLM_MODEL for generic configuration
        model = os.getenv("LLM_MODEL")
        if model:
            return model
        
        # Provider-specific defaults (only for local/mock)
        defaults = {
            LLMProvider.MOCK: "mock-model",
            LLMProvider.OLLAMA: "llama2",
            # Cloud providers have no defaults - require explicit configuration
            LLMProvider.OPENAI: None,
            LLMProvider.ANTHROPIC: None,
            LLMProvider.GOOGLE: None,
            LLMProvider.AZURE_OPENAI: None,
        }
        
        return defaults.get(self.provider)
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment for cloud providers."""
        key_map = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            LLMProvider.GOOGLE: "GOOGLE_API_KEY",
            LLMProvider.AZURE_OPENAI: "AZURE_OPENAI_API_KEY",
        }
        
        if self.provider in key_map:
            return os.getenv(key_map[self.provider])
        return None
    
    def _get_base_url(self) -> str:
        """Get base URL for provider API."""
        env_key = f"{self.provider.value.upper().replace('-', '_')}_BASE_URL"
        env_url = os.getenv(env_key)
        
        if env_url:
            return env_url
        
        # Provider defaults
        defaults = {
            LLMProvider.OLLAMA: "http://localhost:11434",
            LLMProvider.OPENAI: "https://api.openai.com/v1",
            LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1",
            LLMProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1",
            LLMProvider.MOCK: "",
        }
        
        return defaults.get(self.provider, "")
    
    def _get_timeout(self) -> int:
        """Get timeout in seconds."""
        env_key = f"{self.provider.value.upper().replace('-', '_')}_TIMEOUT"
        timeout_str = os.getenv(env_key)
        
        if timeout_str:
            return int(timeout_str)
        
        # Generic fallback
        return int(os.getenv("LLM_TIMEOUT", "60"))
    
    def _get_temperature(self) -> float:
        """Get temperature for generation."""
        env_key = f"{self.provider.value.upper().replace('-', '_')}_TEMPERATURE"
        temp_str = os.getenv(env_key)
        
        if temp_str:
            return float(temp_str)
        
        # Generic fallback
        return float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration completeness.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check model is specified
        if not self.model:
            return False, f"Model not specified for {self.provider.value} (set {self.provider.value.upper()}_MODEL or LLM_MODEL)"
        
        # Check API key for cloud providers
        cloud_providers = [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.GOOGLE,
            LLMProvider.AZURE_OPENAI
        ]
        
        if self.provider in cloud_providers and not self.api_key:
            key_name = f"{self.provider.value.upper().replace('-', '_')}_API_KEY"
            return False, f"API key required for {self.provider.value} (set {key_name})"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "temperature": self.temperature,
            "has_api_key": bool(self.api_key),  # Don't expose actual key
        }


class Config:
    """
    Application configuration (Legacy - use AgentConfig for new code).
    
    Supports environment variable overrides.
    Maintained for backwards compatibility.
    """

    # Current provider (new field)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")

    # LLM Provider defaults
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
    OLLAMA_MODEL: str = os.getenv(
        "OLLAMA_MODEL",
        os.getenv("LLM_MODEL", OllamaModel.LLAMA2.value)
    )
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", os.getenv("LLM_TIMEOUT", "60")))

    # Tool settings
    OLLAMA_TOOLS_TEMPERATURE: float = float(
        os.getenv("OLLAMA_TOOLS_TEMPERATURE", os.getenv("TOOL_TEMPERATURE", "0.3"))
    )
    OLLAMA_TOOLS_MAX_LENGTH: int = int(
        os.getenv("OLLAMA_TOOLS_MAX_LENGTH", "500")
    )

    # Orchestrator settings
    AGENT_MAX_TURNS: int = int(os.getenv("AGENT_MAX_TURNS", "10"))
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "300"))
    
    # Tool timeout (new)
    TOOL_TIMEOUT: int = int(os.getenv("TOOL_TIMEOUT", "30"))

    @classmethod
    def set_ollama_model(cls, model: str) -> None:
        """
        Set the Ollama model at runtime.
        
        Args:
            model: Model name (e.g., "llama2", "mistral:7b", custom name)
        """
        cls.OLLAMA_MODEL = model

    @classmethod
    def get_ollama_model(cls) -> str:
        """
        Get the current Ollama model.
        
        Returns:
            Model name
        """
        return cls.OLLAMA_MODEL

    @classmethod
    def to_dict(cls) -> dict:
        """Get all configuration as dictionary."""
        return {
            "ollama": {
                "base_url": cls.OLLAMA_BASE_URL,
                "model": cls.OLLAMA_MODEL,
                "timeout": cls.OLLAMA_TIMEOUT,
                "temperature": cls.OLLAMA_TOOLS_TEMPERATURE,
                "max_length": cls.OLLAMA_TOOLS_MAX_LENGTH,
            },
            "agent": {
                "max_turns": cls.AGENT_MAX_TURNS,
                "timeout": cls.AGENT_TIMEOUT,
            },
        }


# Export convenience functions
def get_ollama_config() -> dict:
    """Get Ollama configuration."""
    return Config.to_dict()["ollama"]


def set_ollama_model(model: str) -> None:
    """Set the Ollama model."""
    Config.set_ollama_model(model)


def get_ollama_model() -> str:
    """Get the current Ollama model."""
    return Config.get_ollama_model()


class AgentConfig:
    """
    Unified agent configuration with multi-provider support.
    
    This is the recommended configuration class for new code.
    Automatically reads from environment variables and validates settings.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Determine provider
        provider_str = os.getenv("LLM_PROVIDER", "mock").lower()
        try:
            self.provider = LLMProvider(provider_str)
        except ValueError:
            valid_providers = ", ".join([p.value for p in LLMProvider])
            raise ValueError(
                f"Unknown LLM_PROVIDER: '{provider_str}'. "
                f"Valid options: {valid_providers}"
            )
        
        # Load provider-specific config
        self.provider_config = ProviderConfig(self.provider)
        
        # Agent settings
        self.max_turns = int(os.getenv("AGENT_MAX_TURNS", "10"))
        self.agent_timeout = int(os.getenv("AGENT_TIMEOUT", "300"))
        
        # Tool settings
        self.tool_timeout = int(os.getenv("TOOL_TIMEOUT", "30"))
        self.tool_temperature = float(os.getenv("TOOL_TEMPERATURE", "0.3"))
        self.tool_max_length = int(os.getenv("TOOL_MAX_LENGTH", "500"))
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate entire configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.provider_config.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.
        
        Returns:
            Dictionary with all configuration settings
        """
        config_dict = self.provider_config.to_dict()
        config_dict.update({
            "agent": {
                "max_turns": self.max_turns,
                "timeout": self.agent_timeout,
            },
            "tools": {
                "timeout": self.tool_timeout,
                "temperature": self.tool_temperature,
                "max_length": self.tool_max_length,
            }
        })
        return config_dict


# Singleton instance for convenience
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """
    Get singleton configuration instance.
    
    Creates configuration on first call, reuses on subsequent calls.
    Call reload_config() to refresh from environment.
    
    Returns:
        AgentConfig instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _config
    if _config is None:
        _config = AgentConfig()
        # Validate on first load
        valid, error = _config.validate()
        if not valid:
            raise ValueError(f"Configuration invalid: {error}")
    return _config


def reload_config() -> AgentConfig:
    """
    Reload configuration from environment variables.
    
    Useful for testing or when environment changes at runtime.
    
    Returns:
        New AgentConfig instance
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _config
    _config = AgentConfig()
    valid, error = _config.validate()
    if not valid:
        raise ValueError(f"Configuration invalid: {error}")
    return _config


def get_provider_config() -> ProviderConfig:
    """
    Get current provider configuration.
    
    Returns:
        ProviderConfig for active provider
    """
    return get_config().provider_config
