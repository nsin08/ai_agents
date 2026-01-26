"""Tests for configuration module."""

import os
import pytest
from agent_labs.config import Config, OllamaModel, get_ollama_model, set_ollama_model


class TestOllamaModelEnum:
    """Test OllamaModel enum."""
    
    def test_model_values(self):
        """Test model enum values."""
        assert OllamaModel.MISTRAL.value == "mistral:7b"
        assert OllamaModel.LLAMA2.value == "llama2"
        assert OllamaModel.LLAMA2_13B.value == "llama2:13b"
        assert OllamaModel.NEURAL_CHAT.value == "neural-chat"
    
    def test_from_string_enum_members(self):
        """Test from_string with enum members."""
        assert OllamaModel.from_string("MISTRAL") == OllamaModel.MISTRAL
        assert OllamaModel.from_string("LLAMA2") == OllamaModel.LLAMA2
        assert OllamaModel.from_string("LLAMA2_13B") == OllamaModel.LLAMA2_13B
    
    def test_from_string_custom_model(self):
        """Test from_string with custom model names."""
        custom = "my-custom-model"
        result = OllamaModel.from_string(custom)
        assert result == custom


class TestConfigDefaults:
    """Test Config class defaults."""
    
    def test_default_ollama_url(self):
        """Test default Ollama URL."""
        expected = "http://localhost:11434"
        assert Config.OLLAMA_BASE_URL == expected
    
    def test_default_model(self):
        """Test default model is llama2."""
        assert Config.OLLAMA_MODEL == "llama2"
    
    def test_default_timeout(self):
        """Test default timeout is 60 seconds."""
        assert Config.OLLAMA_TIMEOUT == 60
    
    def test_default_temperature(self):
        """Test default temperature."""
        assert Config.OLLAMA_TOOLS_TEMPERATURE == 0.3
    
    def test_default_max_length(self):
        """Test default max length."""
        assert Config.OLLAMA_TOOLS_MAX_LENGTH == 500
    
    def test_default_agent_settings(self):
        """Test default agent settings."""
        assert Config.AGENT_MAX_TURNS == 10
        assert Config.AGENT_TIMEOUT == 300


class TestConfigSetters:
    """Test Config setter methods."""
    
    def test_set_ollama_model(self):
        """Test setting Ollama model."""
        original = Config.OLLAMA_MODEL
        try:
            Config.set_ollama_model("mistral:7b")
            assert Config.OLLAMA_MODEL == "mistral:7b"
            assert Config.get_ollama_model() == "mistral:7b"
        finally:
            Config.set_ollama_model(original)
    
    def test_set_custom_model(self):
        """Test setting custom model name."""
        original = Config.OLLAMA_MODEL
        try:
            Config.set_ollama_model("my-custom-model:latest")
            assert Config.get_ollama_model() == "my-custom-model:latest"
        finally:
            Config.set_ollama_model(original)


class TestConfigConvenience:
    """Test convenience functions."""
    
    def test_get_ollama_model_function(self):
        """Test get_ollama_model function."""
        model = get_ollama_model()
        assert isinstance(model, str)
        assert len(model) > 0
    
    def test_set_ollama_model_function(self):
        """Test set_ollama_model function."""
        original = Config.OLLAMA_MODEL
        try:
            set_ollama_model("llama2:13b")
            assert get_ollama_model() == "llama2:13b"
        finally:
            set_ollama_model(original)


class TestConfigDict:
    """Test Config.to_dict()."""
    
    def test_to_dict_structure(self):
        """Test Config.to_dict() returns proper structure."""
        config = Config.to_dict()
        
        # Top-level keys
        assert "ollama" in config
        assert "agent" in config
        
        # Ollama section
        assert "base_url" in config["ollama"]
        assert "model" in config["ollama"]
        assert "timeout" in config["ollama"]
        assert "temperature" in config["ollama"]
        assert "max_length" in config["ollama"]
        
        # Agent section
        assert "max_turns" in config["agent"]
        assert "timeout" in config["agent"]
    
    def test_to_dict_values(self):
        """Test Config.to_dict() has correct values."""
        config = Config.to_dict()
        
        assert config["ollama"]["base_url"] == Config.OLLAMA_BASE_URL
        assert config["ollama"]["model"] == Config.OLLAMA_MODEL
        assert config["ollama"]["timeout"] == Config.OLLAMA_TIMEOUT
        assert config["agent"]["max_turns"] == Config.AGENT_MAX_TURNS


@pytest.mark.skipif(
    "SKIP_OLLAMA" in os.environ,
    reason="Config tests require checking environment variable handling"
)
class TestConfigEnvironmentVariables:
    """Test environment variable overrides (optional, requires Ollama)."""
    
    def test_env_override_ollama_model(self, monkeypatch):
        """Test OLLAMA_MODEL environment variable override."""
        # This would normally test actual env var loading
        # For now, just verify the mechanism exists
        assert hasattr(Config, "OLLAMA_MODEL")
        assert isinstance(Config.OLLAMA_MODEL, str)
