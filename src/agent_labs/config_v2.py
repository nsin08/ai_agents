"""
Enhanced configuration system with YAML support and precedence-based loading.

Implements configuration precedence: Explicit > Env > File > Default

Features:
- Pydantic v2 validation with JSON Schema export
- YAML file loading with merge support
- Multiple config sections: app, mode, models, tools, memory, engine, observability
- Secure secret handling (API keys from env vars only)
- Clear error messages for validation failures
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ConfigError(Exception):
    """Configuration error with clear error message."""

    pass


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure-openai"


class AppMode(str, Enum):
    """Application execution mode."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class AppConfig(BaseModel):
    """Application-level configuration."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(default="ai_agent", description="Application name")
    mode: AppMode = Field(default=AppMode.DEVELOPMENT, description="Execution mode")
    debug: bool = Field(default=False, description="Enable debug logging")
    log_level: str = Field(default="INFO", description="Logging level")


class ModelConfig(BaseModel):
    """LLM model configuration."""

    model_config = ConfigDict(extra="forbid")

    provider: LLMProvider = Field(default=LLMProvider.MOCK, description="LLM provider")
    model: Optional[str] = Field(default=None, description="Model name/identifier")
    base_url: Optional[str] = Field(default=None, description="API base URL")
    timeout: int = Field(default=60, ge=1, le=600, description="Request timeout in seconds")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Max tokens to generate")

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: Optional[str], info) -> Optional[str]:
        """Validate model is set for non-mock providers."""
        if v is None:
            provider = info.data.get("provider", LLMProvider.MOCK)
            if provider != LLMProvider.MOCK:
                # Will be validated in model_validator
                pass
        return v

    @model_validator(mode="after")
    def validate_provider_requirements(self):
        """Validate provider-specific requirements."""
        # Model name required for non-mock providers
        if self.provider != LLMProvider.MOCK and not self.model:
            raise ConfigError(
                f"Model name required for provider '{self.provider.value}'. "
                f"Set via MODEL field or {self.provider.value.upper()}_MODEL env var."
            )

        # Set default base URLs for providers
        if not self.base_url:
            defaults = {
                LLMProvider.OLLAMA: "http://localhost:11434",
                LLMProvider.OPENAI: "https://api.openai.com/v1",
                LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1",
                LLMProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1",
                LLMProvider.MOCK: "",
            }
            self.base_url = defaults.get(self.provider, "")

        # Set default model for mock
        if self.provider == LLMProvider.MOCK and not self.model:
            self.model = "mock-model"

        return self


class ToolsConfig(BaseModel):
    """Tool execution configuration."""

    model_config = ConfigDict(extra="forbid")

    timeout: int = Field(default=30, ge=1, le=300, description="Tool timeout in seconds")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Tool LLM temperature")
    max_length: int = Field(default=500, ge=1, description="Max tool output length")
    allowlist: Optional[List[str]] = Field(default=None, description="Allowed tool names")


class MemoryConfig(BaseModel):
    """Memory and context configuration."""

    model_config = ConfigDict(extra="forbid")

    short_term_size: int = Field(default=10, ge=1, description="Short-term memory size")
    long_term_enabled: bool = Field(default=False, description="Enable long-term memory")
    context_window: int = Field(default=4096, ge=512, description="Context window size")


class EngineConfig(BaseModel):
    """Agent orchestration engine configuration."""

    model_config = ConfigDict(extra="forbid")

    max_turns: int = Field(default=10, ge=1, le=100, description="Max reasoning turns")
    timeout: int = Field(default=300, ge=1, le=3600, description="Agent timeout in seconds")
    enable_reflection: bool = Field(default=True, description="Enable reflection step")


class ObservabilityConfig(BaseModel):
    """Observability and monitoring configuration."""

    model_config = ConfigDict(extra="forbid")

    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")
    enable_metrics: bool = Field(default=False, description="Enable metrics collection")
    log_prompts: bool = Field(default=False, description="Log LLM prompts")
    log_responses: bool = Field(default=False, description="Log LLM responses")


class AgentConfig(BaseModel):
    """
    Unified agent configuration with multi-source loading.

    Configuration precedence: Explicit params > Env vars > YAML file > Defaults

    Example:
        # Load from defaults
        config = AgentConfig()

        # Load from YAML file
        config = AgentConfig.from_yaml("config/local.yaml")

        # Load with explicit overrides
        config = AgentConfig.from_yaml("config/local.yaml", models={"provider": "openai"})

        # Load from environment only
        config = AgentConfig.from_env()
    """

    model_config = ConfigDict(extra="forbid")

    app: AppConfig = Field(default_factory=AppConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    engine: EngineConfig = Field(default_factory=EngineConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str | Path, **overrides) -> "AgentConfig":
        """
        Load configuration from YAML file with optional overrides.

        Precedence: overrides > env vars > yaml file > defaults

        Args:
            yaml_path: Path to YAML configuration file
            **overrides: Explicit parameter overrides (e.g., models={"provider": "openai"})

        Returns:
            AgentConfig instance

        Raises:
            ConfigError: If file not found or invalid YAML
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise ConfigError(f"Configuration file not found: {yaml_path}")

        try:
            with open(yaml_path, "r") as f:
                yaml_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {yaml_path}: {e}")

        # Merge: YAML < Env < Explicit
        merged = cls._merge_configs(yaml_data, cls._load_from_env(), overrides)

        try:
            return cls(**merged)
        except Exception as e:
            raise ConfigError(f"Configuration validation failed: {e}")

    @classmethod
    def from_env(cls, **overrides) -> "AgentConfig":
        """
        Load configuration from environment variables only.

        Args:
            **overrides: Explicit parameter overrides

        Returns:
            AgentConfig instance
        """
        env_data = cls._load_from_env()
        merged = cls._merge_configs(env_data, overrides)

        try:
            return cls(**merged)
        except Exception as e:
            raise ConfigError(f"Configuration validation failed: {e}")

    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        # App section
        if os.getenv("APP_NAME"):
            config.setdefault("app", {})["name"] = os.getenv("APP_NAME")
        if os.getenv("APP_MODE"):
            config.setdefault("app", {})["mode"] = os.getenv("APP_MODE")
        if os.getenv("APP_DEBUG"):
            config.setdefault("app", {})["debug"] = os.getenv("APP_DEBUG").lower() == "true"
        if os.getenv("LOG_LEVEL"):
            config.setdefault("app", {})["log_level"] = os.getenv("LOG_LEVEL")

        # Models section
        if os.getenv("LLM_PROVIDER") or os.getenv("MODEL_PROVIDER"):
            provider = os.getenv("MODEL_PROVIDER") or os.getenv("LLM_PROVIDER")
            config.setdefault("models", {})["provider"] = provider

        if os.getenv("LLM_MODEL"):
            config.setdefault("models", {})["model"] = os.getenv("LLM_MODEL")

        # Provider-specific model env vars
        provider = config.get("models", {}).get("provider", "")
        if provider:
            provider_upper = provider.upper().replace("-", "_")
            model_key = f"{provider_upper}_MODEL"
            if os.getenv(model_key):
                config.setdefault("models", {})["model"] = os.getenv(model_key)

        if os.getenv("LLM_BASE_URL"):
            config.setdefault("models", {})["base_url"] = os.getenv("LLM_BASE_URL")
        if os.getenv("LLM_TIMEOUT"):
            config.setdefault("models", {})["timeout"] = int(os.getenv("LLM_TIMEOUT"))
        if os.getenv("LLM_TEMPERATURE"):
            config.setdefault("models", {})["temperature"] = float(os.getenv("LLM_TEMPERATURE"))
        if os.getenv("LLM_MAX_TOKENS"):
            config.setdefault("models", {})["max_tokens"] = int(os.getenv("LLM_MAX_TOKENS"))

        # Tools section
        if os.getenv("TOOL_TIMEOUT"):
            config.setdefault("tools", {})["timeout"] = int(os.getenv("TOOL_TIMEOUT"))
        if os.getenv("TOOL_TEMPERATURE"):
            config.setdefault("tools", {})["temperature"] = float(os.getenv("TOOL_TEMPERATURE"))
        if os.getenv("TOOL_MAX_LENGTH"):
            config.setdefault("tools", {})["max_length"] = int(os.getenv("TOOL_MAX_LENGTH"))
        if os.getenv("TOOL_ALLOWLIST"):
            allowlist = os.getenv("TOOL_ALLOWLIST").split(",")
            config.setdefault("tools", {})["allowlist"] = [t.strip() for t in allowlist]

        # Memory section
        if os.getenv("MEMORY_SHORT_TERM_SIZE"):
            config.setdefault("memory", {})["short_term_size"] = int(
                os.getenv("MEMORY_SHORT_TERM_SIZE")
            )
        if os.getenv("MEMORY_LONG_TERM_ENABLED"):
            config.setdefault("memory", {})["long_term_enabled"] = (
                os.getenv("MEMORY_LONG_TERM_ENABLED").lower() == "true"
            )
        if os.getenv("MEMORY_CONTEXT_WINDOW"):
            config.setdefault("memory", {})["context_window"] = int(
                os.getenv("MEMORY_CONTEXT_WINDOW")
            )

        # Engine section
        if os.getenv("AGENT_MAX_TURNS"):
            config.setdefault("engine", {})["max_turns"] = int(os.getenv("AGENT_MAX_TURNS"))
        if os.getenv("AGENT_TIMEOUT"):
            config.setdefault("engine", {})["timeout"] = int(os.getenv("AGENT_TIMEOUT"))
        if os.getenv("AGENT_ENABLE_REFLECTION"):
            config.setdefault("engine", {})["enable_reflection"] = (
                os.getenv("AGENT_ENABLE_REFLECTION").lower() == "true"
            )

        # Observability section
        if os.getenv("OBSERVABILITY_ENABLE_TRACING"):
            config.setdefault("observability", {})["enable_tracing"] = (
                os.getenv("OBSERVABILITY_ENABLE_TRACING").lower() == "true"
            )
        if os.getenv("OBSERVABILITY_ENABLE_METRICS"):
            config.setdefault("observability", {})["enable_metrics"] = (
                os.getenv("OBSERVABILITY_ENABLE_METRICS").lower() == "true"
            )
        if os.getenv("OBSERVABILITY_LOG_PROMPTS"):
            config.setdefault("observability", {})["log_prompts"] = (
                os.getenv("OBSERVABILITY_LOG_PROMPTS").lower() == "true"
            )
        if os.getenv("OBSERVABILITY_LOG_RESPONSES"):
            config.setdefault("observability", {})["log_responses"] = (
                os.getenv("OBSERVABILITY_LOG_RESPONSES").lower() == "true"
            )

        return config

    @staticmethod
    def _merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Later configs override earlier configs. Nested dicts are merged recursively.

        Args:
            *configs: Configuration dictionaries to merge

        Returns:
            Merged configuration dictionary
        """
        result = {}

        for config in configs:
            if not config:
                continue

            for key, value in config.items():
                if key not in result:
                    result[key] = value
                elif isinstance(value, dict) and isinstance(result[key], dict):
                    # Recursive merge for nested dicts
                    result[key] = AgentConfig._merge_configs(result[key], value)
                else:
                    # Override
                    result[key] = value

        return result

    def validate_secrets(self) -> None:
        """
        Validate that API keys are loaded from environment, not config files.

        Raises:
            ConfigError: If security validation fails
        """
        cloud_providers = [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.GOOGLE,
            LLMProvider.AZURE_OPENAI,
        ]

        if self.models.provider in cloud_providers:
            # Check that API key is available in environment
            key_map = {
                LLMProvider.OPENAI: "OPENAI_API_KEY",
                LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
                LLMProvider.GOOGLE: "GOOGLE_API_KEY",
                LLMProvider.AZURE_OPENAI: "AZURE_OPENAI_API_KEY",
            }

            key_name = key_map[self.models.provider]
            if not os.getenv(key_name):
                raise ConfigError(
                    f"API key required for {self.models.provider.value}. "
                    f"Set {key_name} environment variable. "
                    f"Never store API keys in configuration files!"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self.model_dump()

    def to_json_schema(self) -> Dict[str, Any]:
        """Export JSON Schema for configuration validation."""
        return self.model_json_schema()


# Convenience functions for backward compatibility
def get_config() -> AgentConfig:
    """
    Get configuration instance from environment.

    Returns:
        AgentConfig loaded from environment variables
    """
    return AgentConfig.from_env()


def load_config(yaml_path: Optional[str] = None, **overrides) -> AgentConfig:
    """
    Load configuration with optional YAML file and overrides.

    Args:
        yaml_path: Optional path to YAML configuration file
        **overrides: Explicit parameter overrides

    Returns:
        AgentConfig instance
    """
    if yaml_path:
        return AgentConfig.from_yaml(yaml_path, **overrides)
    return AgentConfig.from_env(**overrides)
