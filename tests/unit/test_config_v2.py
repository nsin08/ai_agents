"""Comprehensive tests for enhanced configuration system (config_v2.py)."""

import os
import pytest
import tempfile
from pathlib import Path
from agent_labs.config_v2 import (
    AgentConfig,
    AppConfig,
    ModelConfig,
    ToolsConfig,
    MemoryConfig,
    EngineConfig,
    ObservabilityConfig,
    LLMProvider,
    AppMode,
    ConfigError,
    get_config,
    load_config,
)


class TestConfigPrecedence:
    """Test configuration precedence: Explicit > Env > File > Default."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AgentConfig()
        
        assert config.app.name == "ai_agent"
        assert config.app.mode == AppMode.DEVELOPMENT
        assert config.models.provider == LLMProvider.MOCK
        assert config.models.timeout == 60
        assert config.tools.timeout == 30
        assert config.engine.max_turns == 10
    
    def test_env_overrides_default(self, monkeypatch):
        """Test environment variables override defaults."""
        monkeypatch.setenv("APP_NAME", "test_agent")
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("LLM_MODEL", "mistral:7b")
        monkeypatch.setenv("AGENT_MAX_TURNS", "15")
        
        config = AgentConfig.from_env()
        
        assert config.app.name == "test_agent"
        assert config.models.provider == LLMProvider.OLLAMA
        assert config.models.model == "mistral:7b"
        assert config.engine.max_turns == 15
    
    def test_yaml_overrides_default(self, tmp_path):
        """Test YAML file overrides defaults."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
app:
  name: yaml_agent
  mode: staging

models:
  provider: openai
  model: gpt-4
  timeout: 90
""")
        
        config = AgentConfig.from_yaml(yaml_file)
        
        assert config.app.name == "yaml_agent"
        assert config.app.mode == AppMode.STAGING
        assert config.models.provider == LLMProvider.OPENAI
        assert config.models.model == "gpt-4"
        assert config.models.timeout == 90
    
    def test_explicit_overrides_yaml(self, tmp_path):
        """Test explicit parameters override YAML."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
models:
  provider: ollama
  model: llama2
  timeout: 60
""")
        
        config = AgentConfig.from_yaml(
            yaml_file,
            models={"provider": "openai", "model": "gpt-4"}
        )
        
        assert config.models.provider == LLMProvider.OPENAI
        assert config.models.model == "gpt-4"
        # Timeout from YAML is preserved (not overridden)
        assert config.models.timeout == 60
    
    def test_explicit_overrides_env(self, monkeypatch):
        """Test explicit parameters override environment."""
        monkeypatch.setenv("APP_NAME", "env_agent")
        monkeypatch.setenv("AGENT_MAX_TURNS", "15")
        
        config = AgentConfig.from_env(
            app={"name": "explicit_agent"},
            engine={"max_turns": 20}
        )
        
        assert config.app.name == "explicit_agent"
        assert config.engine.max_turns == 20
    
    def test_full_precedence_chain(self, tmp_path, monkeypatch):
        """Test full precedence: Explicit > Env > YAML > Default."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
app:
  name: yaml_agent
  mode: development

models:
  provider: ollama
  model: llama2
  timeout: 60

engine:
  max_turns: 10
  timeout: 300
""")
        
        monkeypatch.setenv("APP_NAME", "env_agent")
        monkeypatch.setenv("AGENT_MAX_TURNS", "15")
        
        config = AgentConfig.from_yaml(
            yaml_file,
            app={"name": "explicit_agent"}
        )
        
        # Explicit wins
        assert config.app.name == "explicit_agent"
        # Env wins over YAML
        assert config.engine.max_turns == 15
        # YAML wins over default
        assert config.models.model == "llama2"
        assert config.engine.timeout == 300


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_model_required_for_cloud_providers(self):
        """Test model name required for cloud providers."""
        with pytest.raises(ConfigError, match="Model name required"):
            AgentConfig(models={"provider": "openai"})
    
    def test_model_optional_for_mock(self):
        """Test model optional for mock provider."""
        config = AgentConfig(models={"provider": "mock"})
        assert config.models.model == "mock-model"
    
    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(models={"provider": "invalid"})
    
    def test_invalid_mode(self):
        """Test invalid mode raises error."""
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(app={"mode": "invalid"})
    
    def test_timeout_bounds(self):
        """Test timeout validation bounds."""
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(models={"timeout": 0})
        
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(models={"timeout": 700})
    
    def test_temperature_bounds(self):
        """Test temperature validation bounds."""
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(models={"temperature": -0.1})
        
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(models={"temperature": 2.1})
    
    def test_extra_fields_forbidden(self):
        """Test extra fields are rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            AgentConfig(models={"unknown_field": "value"})


class TestYAMLLoading:
    """Test YAML file loading."""
    
    def test_load_nonexistent_file(self):
        """Test error when file doesn't exist."""
        with pytest.raises(ConfigError, match="not found"):
            AgentConfig.from_yaml("/nonexistent/file.yaml")
    
    def test_load_invalid_yaml(self, tmp_path):
        """Test error with invalid YAML syntax."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: syntax:")
        
        with pytest.raises(ConfigError, match="Invalid YAML"):
            AgentConfig.from_yaml(yaml_file)
    
    def test_load_empty_yaml(self, tmp_path):
        """Test loading empty YAML file uses defaults."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        
        config = AgentConfig.from_yaml(yaml_file)
        assert config.app.name == "ai_agent"
    
    def test_load_example_configs(self):
        """Test loading example configuration files."""
        base_path = Path("/home/runner/work/ai_agents/ai_agents/config")
        
        if (base_path / "local.yaml").exists():
            config = AgentConfig.from_yaml(base_path / "local.yaml")
            assert config.models.provider == LLMProvider.OLLAMA
            assert config.app.mode == AppMode.DEVELOPMENT
        
        if (base_path / "staging.yaml").exists():
            config = AgentConfig.from_yaml(base_path / "staging.yaml")
            assert config.models.provider == LLMProvider.OPENAI
            assert config.app.mode == AppMode.STAGING


class TestEnvVarMapping:
    """Test environment variable mapping."""
    
    def test_app_env_vars(self, monkeypatch):
        """Test APP_* environment variables."""
        monkeypatch.setenv("APP_NAME", "my_agent")
        monkeypatch.setenv("APP_MODE", "production")
        monkeypatch.setenv("APP_DEBUG", "true")
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        
        config = AgentConfig.from_env()
        
        assert config.app.name == "my_agent"
        assert config.app.mode == AppMode.PRODUCTION
        assert config.app.debug is True
        assert config.app.log_level == "ERROR"
    
    def test_model_env_vars(self, monkeypatch):
        """Test MODEL_* and LLM_* environment variables."""
        monkeypatch.setenv("MODEL_PROVIDER", "openai")
        monkeypatch.setenv("LLM_MODEL", "gpt-4")
        monkeypatch.setenv("LLM_BASE_URL", "https://custom.api.com")
        monkeypatch.setenv("LLM_TIMEOUT", "45")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.5")
        
        config = AgentConfig.from_env()
        
        assert config.models.provider == LLMProvider.OPENAI
        assert config.models.model == "gpt-4"
        assert config.models.base_url == "https://custom.api.com"
        assert config.models.timeout == 45
        assert config.models.temperature == 0.5
    
    def test_provider_specific_model_env(self, monkeypatch):
        """Test provider-specific MODEL env vars."""
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_MODEL", "mistral:7b")
        
        config = AgentConfig.from_env()
        
        assert config.models.model == "mistral:7b"
    
    def test_tool_env_vars(self, monkeypatch):
        """Test TOOL_* environment variables."""
        monkeypatch.setenv("TOOL_TIMEOUT", "45")
        monkeypatch.setenv("TOOL_TEMPERATURE", "0.2")
        monkeypatch.setenv("TOOL_MAX_LENGTH", "1000")
        monkeypatch.setenv("TOOL_ALLOWLIST", "calculator,web_search,file_read")
        
        config = AgentConfig.from_env()
        
        assert config.tools.timeout == 45
        assert config.tools.temperature == 0.2
        assert config.tools.max_length == 1000
        assert config.tools.allowlist == ["calculator", "web_search", "file_read"]
    
    def test_memory_env_vars(self, monkeypatch):
        """Test MEMORY_* environment variables."""
        monkeypatch.setenv("MEMORY_SHORT_TERM_SIZE", "20")
        monkeypatch.setenv("MEMORY_LONG_TERM_ENABLED", "true")
        monkeypatch.setenv("MEMORY_CONTEXT_WINDOW", "8192")
        
        config = AgentConfig.from_env()
        
        assert config.memory.short_term_size == 20
        assert config.memory.long_term_enabled is True
        assert config.memory.context_window == 8192
    
    def test_engine_env_vars(self, monkeypatch):
        """Test AGENT_* (engine) environment variables."""
        monkeypatch.setenv("AGENT_MAX_TURNS", "25")
        monkeypatch.setenv("AGENT_TIMEOUT", "600")
        monkeypatch.setenv("AGENT_ENABLE_REFLECTION", "false")
        
        config = AgentConfig.from_env()
        
        assert config.engine.max_turns == 25
        assert config.engine.timeout == 600
        assert config.engine.enable_reflection is False
    
    def test_observability_env_vars(self, monkeypatch):
        """Test OBSERVABILITY_* environment variables."""
        monkeypatch.setenv("OBSERVABILITY_ENABLE_TRACING", "true")
        monkeypatch.setenv("OBSERVABILITY_ENABLE_METRICS", "true")
        monkeypatch.setenv("OBSERVABILITY_LOG_PROMPTS", "true")
        monkeypatch.setenv("OBSERVABILITY_LOG_RESPONSES", "false")
        
        config = AgentConfig.from_env()
        
        assert config.observability.enable_tracing is True
        assert config.observability.enable_metrics is True
        assert config.observability.log_prompts is True
        assert config.observability.log_responses is False


class TestConfigSections:
    """Test individual configuration sections."""
    
    def test_app_section(self):
        """Test AppConfig section."""
        config = AgentConfig(app={
            "name": "test_app",
            "mode": "production",
            "debug": False,
            "log_level": "INFO"
        })
        
        assert config.app.name == "test_app"
        assert config.app.mode == AppMode.PRODUCTION
        assert config.app.debug is False
        assert config.app.log_level == "INFO"
    
    def test_models_section(self):
        """Test ModelConfig section."""
        config = AgentConfig(models={
            "provider": "ollama",
            "model": "llama2",
            "base_url": "http://localhost:11434",
            "timeout": 60,
            "temperature": 0.7,
            "max_tokens": 2048
        })
        
        assert config.models.provider == LLMProvider.OLLAMA
        assert config.models.model == "llama2"
        assert config.models.max_tokens == 2048
    
    def test_tools_section(self):
        """Test ToolsConfig section."""
        config = AgentConfig(tools={
            "timeout": 45,
            "temperature": 0.2,
            "max_length": 1000,
            "allowlist": ["calculator", "web_search"]
        })
        
        assert config.tools.timeout == 45
        assert config.tools.allowlist == ["calculator", "web_search"]
    
    def test_memory_section(self):
        """Test MemoryConfig section."""
        config = AgentConfig(memory={
            "short_term_size": 20,
            "long_term_enabled": True,
            "context_window": 8192
        })
        
        assert config.memory.short_term_size == 20
        assert config.memory.long_term_enabled is True
        assert config.memory.context_window == 8192
    
    def test_engine_section(self):
        """Test EngineConfig section."""
        config = AgentConfig(engine={
            "max_turns": 20,
            "timeout": 600,
            "enable_reflection": False
        })
        
        assert config.engine.max_turns == 20
        assert config.engine.timeout == 600
        assert config.engine.enable_reflection is False
    
    def test_observability_section(self):
        """Test ObservabilityConfig section."""
        config = AgentConfig(observability={
            "enable_tracing": True,
            "enable_metrics": True,
            "log_prompts": False,
            "log_responses": False
        })
        
        assert config.observability.enable_tracing is True
        assert config.observability.log_prompts is False


class TestSecurityValidation:
    """Test security-related validation."""
    
    def test_api_key_required_for_openai(self, monkeypatch):
        """Test API key validation for OpenAI."""
        # Clear any existing key
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        config = AgentConfig(models={"provider": "openai", "model": "gpt-4"})
        
        with pytest.raises(ConfigError, match="API key required"):
            config.validate_secrets()
    
    def test_api_key_present_for_openai(self, monkeypatch):
        """Test API key validation passes when key is set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        
        config = AgentConfig(models={"provider": "openai", "model": "gpt-4"})
        
        # Should not raise
        config.validate_secrets()
    
    def test_no_api_key_required_for_ollama(self):
        """Test no API key required for local providers."""
        config = AgentConfig(models={"provider": "ollama", "model": "llama2"})
        
        # Should not raise
        config.validate_secrets()
    
    def test_api_key_required_for_anthropic(self, monkeypatch):
        """Test API key validation for Anthropic."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        config = AgentConfig(models={"provider": "anthropic", "model": "claude-3"})
        
        with pytest.raises(ConfigError, match="API key required"):
            config.validate_secrets()


class TestConfigExport:
    """Test configuration export functionality."""
    
    def test_to_dict(self):
        """Test exporting config to dictionary."""
        config = AgentConfig(
            app={"name": "test_agent"},
            models={"provider": "mock"}
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "app" in config_dict
        assert "models" in config_dict
        assert config_dict["app"]["name"] == "test_agent"
    
    def test_to_json_schema(self):
        """Test JSON schema export."""
        schema = AgentConfig().to_json_schema()
        
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "app" in schema["properties"]
        assert "models" in schema["properties"]


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_config(self, monkeypatch):
        """Test get_config function."""
        monkeypatch.setenv("APP_NAME", "convenience_test")
        
        config = get_config()
        
        assert isinstance(config, AgentConfig)
        assert config.app.name == "convenience_test"
    
    def test_load_config_with_yaml(self, tmp_path):
        """Test load_config with YAML file."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
app:
  name: yaml_test
""")
        
        config = load_config(str(yaml_file))
        
        assert config.app.name == "yaml_test"
    
    def test_load_config_without_yaml(self, monkeypatch):
        """Test load_config without YAML file."""
        monkeypatch.setenv("APP_NAME", "env_test")
        
        config = load_config()
        
        assert config.app.name == "env_test"


class TestConfigMerge:
    """Test configuration merging logic."""
    
    def test_merge_simple_override(self):
        """Test simple value override in merge."""
        config1 = {"app": {"name": "first"}}
        config2 = {"app": {"name": "second"}}
        
        merged = AgentConfig._merge_configs(config1, config2)
        
        assert merged["app"]["name"] == "second"
    
    def test_merge_nested_preserve(self):
        """Test nested values are preserved in merge."""
        config1 = {"app": {"name": "first", "mode": "development"}}
        config2 = {"app": {"name": "second"}}
        
        merged = AgentConfig._merge_configs(config1, config2)
        
        assert merged["app"]["name"] == "second"
        assert merged["app"]["mode"] == "development"
    
    def test_merge_multiple_configs(self):
        """Test merging multiple configurations."""
        config1 = {"app": {"name": "first"}}
        config2 = {"app": {"mode": "staging"}}
        config3 = {"models": {"provider": "openai"}}
        
        merged = AgentConfig._merge_configs(config1, config2, config3)
        
        assert merged["app"]["name"] == "first"
        assert merged["app"]["mode"] == "staging"
        assert merged["models"]["provider"] == "openai"
