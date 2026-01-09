"""
Configuration management for agent_labs.

Provides centralized configuration for LLM models, providers, and tool settings.
"""

import os
from typing import Optional
from enum import Enum


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


class Config:
    """
    Application configuration.
    
    Supports environment variable overrides.
    """

    # LLM Provider defaults
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
    OLLAMA_MODEL: str = os.getenv(
        "OLLAMA_MODEL",
        OllamaModel.LLAMA2.value
    )
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))

    # Tool settings
    OLLAMA_TOOLS_TEMPERATURE: float = float(
        os.getenv("OLLAMA_TOOLS_TEMPERATURE", "0.3")
    )
    OLLAMA_TOOLS_MAX_LENGTH: int = int(
        os.getenv("OLLAMA_TOOLS_MAX_LENGTH", "500")
    )

    # Orchestrator settings
    AGENT_MAX_TURNS: int = int(os.getenv("AGENT_MAX_TURNS", "10"))
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "300"))

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
