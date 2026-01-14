# Architecture Review: Configuration Hardcoding Issues

**Date**: 2026-01-14  
**Reviewer**: AI Architect  
**Scope**: scripts/, labs/, src/ directories  
**Issue**: Hardcoded model names and configuration values

---

## Executive Summary

**Finding**: Multiple hardcoded model names and configuration values across 15+ files violate the Single Source of Truth principle and create maintenance burden.

**Impact**: 
- 🔴 **High**: Configuration changes require multi-file updates
- 🟡 **Medium**: Testing different models requires code modifications
- 🟡 **Medium**: Cloud provider integration blocked by hardcoded values

**Recommendation**: Implement unified configuration system with environment-based overrides following 12-factor app principles.

---

## Findings

### 1. Hardcoded Model Names

**Location**: `scripts/interactive_agent.py`
```python
# Line 57: Hardcoded default
self.model_name = "mistral:7b"
```

**Location**: `scripts/advanced_interactive_agent.py`
```python
# Line 259: Partial fix with env var but hardcoded fallback
self.model_name = os.getenv("OLLAMA_MODEL", "mistral:7b")
```

**Location**: `labs/05/src/context_agent.py`
```python
# Line 52: Hardcoded OpenAI model
def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 8000):
```

**Location**: `labs/00/src/hello_agent.py`
```python
# Line 17: Better pattern but still has fallback
model=os.getenv("OLLAMA_MODEL", "llama2"),
```

### 2. Missing Provider Support

**Gap**: No configuration for cloud providers (OpenAI, Anthropic, Google)
- Missing API key management
- No provider-specific authentication patterns
- No model-to-provider mapping

### 3. Inconsistent Configuration Patterns

**Pattern A** (Good): `src/agent_labs/config.py`
- Centralized Config class
- Environment variable support
- Runtime setter methods

**Pattern B** (Inconsistent): Direct `os.getenv()` calls
- Scattered across multiple files
- Different default values
- No validation

**Pattern C** (Legacy): Hardcoded strings
- No configurability
- Copy-paste across files

### 4. Labs Curriculum Issues

**Lab 5 (Context Agent)**: Hardcoded `gpt-3.5-turbo` in 4 locations
- Constructor default
- Test assertions (lines 57, 63, 64, 283)
- No way to test with different models

**Lab 1 (RAG)**: Ollama-only with hardcoded defaults
- No mock provider option for CI/CD
- Requires running Ollama server for testing

---

## Proposed Architecture

### Design Principles

1. **Single Source of Truth**: One config module, one source
2. **Environment-First**: Use env vars (12-factor app)
3. **Secure by Default**: No credentials in code or defaults
4. **Provider-Agnostic**: Support multiple LLM providers
5. **Testable**: Mock configurations for CI/CD

### Unified Configuration System

```python
# src/agent_labs/config.py (Enhanced)

from typing import Optional, Dict, Any
from enum import Enum
import os


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure-openai"


class ProviderConfig:
    """Provider-specific configuration."""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.model = self._get_model()
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.timeout = self._get_timeout()
        self.temperature = self._get_temperature()
    
    def _get_model(self) -> str:
        """Get model name from env with provider-specific defaults."""
        env_key = f"{self.provider.value.upper()}_MODEL"
        
        defaults = {
            LLMProvider.MOCK: "mock-model",
            LLMProvider.OLLAMA: "llama2",
            LLMProvider.OPENAI: None,  # Force user to specify
            LLMProvider.ANTHROPIC: None,
            LLMProvider.GOOGLE: None,
            LLMProvider.AZURE_OPENAI: None,
        }
        
        return os.getenv(env_key, defaults.get(self.provider))
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
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
        """Get base URL for provider."""
        env_key = f"{self.provider.value.upper()}_BASE_URL"
        
        defaults = {
            LLMProvider.OLLAMA: "http://localhost:11434",
            LLMProvider.OPENAI: "https://api.openai.com/v1",
            LLMProvider.ANTHROPIC: "https://api.anthropic.com",
            LLMProvider.GOOGLE: "https://generativelanguage.googleapis.com",
        }
        
        return os.getenv(env_key, defaults.get(self.provider, ""))
    
    def _get_timeout(self) -> int:
        """Get timeout in seconds."""
        env_key = f"{self.provider.value.upper()}_TIMEOUT"
        return int(os.getenv(env_key, "60"))
    
    def _get_temperature(self) -> float:
        """Get temperature for generation."""
        env_key = f"{self.provider.value.upper()}_TEMPERATURE"
        return float(os.getenv(env_key, "0.7"))
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate configuration."""
        # Check model is set
        if not self.model:
            return False, f"Model not specified for {self.provider.value}"
        
        # Check API key for cloud providers
        if self.provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, 
                            LLMProvider.GOOGLE, LLMProvider.AZURE_OPENAI]:
            if not self.api_key:
                return False, f"API key required for {self.provider.value}"
        
        return True, None


class AgentConfig:
    """Unified agent configuration."""
    
    def __init__(self):
        # Determine provider
        provider_str = os.getenv("LLM_PROVIDER", "mock").lower()
        try:
            self.provider = LLMProvider(provider_str)
        except ValueError:
            raise ValueError(f"Unknown provider: {provider_str}")
        
        # Load provider config
        self.provider_config = ProviderConfig(self.provider)
        
        # Agent settings
        self.max_turns = int(os.getenv("AGENT_MAX_TURNS", "10"))
        self.agent_timeout = int(os.getenv("AGENT_TIMEOUT", "300"))
        
        # Tool settings
        self.tool_timeout = int(os.getenv("TOOL_TIMEOUT", "30"))
        self.tool_temperature = float(os.getenv("TOOL_TEMPERATURE", "0.3"))
        
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate entire configuration."""
        return self.provider_config.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.provider_config.model,
            "base_url": self.provider_config.base_url,
            "timeout": self.provider_config.timeout,
            "temperature": self.provider_config.temperature,
            "agent": {
                "max_turns": self.max_turns,
                "timeout": self.agent_timeout,
            },
            "tools": {
                "timeout": self.tool_timeout,
                "temperature": self.tool_temperature,
            }
        }


# Singleton instance
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get singleton configuration instance."""
    global _config
    if _config is None:
        _config = AgentConfig()
    return _config


def reload_config() -> AgentConfig:
    """Reload configuration from environment."""
    global _config
    _config = AgentConfig()
    return _config
```

---

## Migration Plan

### Phase 1: Core Infrastructure (High Priority)

**Files to Update**:
1. ✅ `src/agent_labs/config.py` - Enhance with ProviderConfig
2. ✅ `src/agent_labs/llm_providers/__init__.py` - Add factory pattern
3. ✅ `.env.example` - Document all env vars

**Pattern**:
```python
# Before (Hardcoded)
provider = OllamaProvider(model="mistral:7b", base_url="http://localhost:11434")

# After (Configurable)
from agent_labs.config import get_config
config = get_config()
provider = create_provider(config.provider, config.provider_config)
```

### Phase 2: Scripts (Medium Priority)

**Files to Update**:
1. `scripts/interactive_agent.py` (line 57)
2. `scripts/advanced_interactive_agent.py` (line 259)
3. `scripts/explore.py` (if applicable)

**Changes**:
- Remove hardcoded `self.model_name = "mistral:7b"`
- Use `config.provider_config.model`
- Support dynamic provider switching via config

### Phase 3: Labs (Medium Priority)

**Files to Update**:
1. `labs/05/src/context_agent.py` (line 52)
   - Change default from `"gpt-3.5-turbo"` to `None`
   - Read from config or require explicit parameter
2. `labs/05/tests/test_context_agent.py` (lines 57, 63, 64, 283)
   - Parameterize model names
   - Use config or fixtures
3. `labs/00/src/hello_agent.py` (line 17)
   - Use config module instead of direct os.getenv
4. `labs/01/src/rag_eval.py` (line 17)
   - Use config module

**Pattern**:
```python
# Before (Lab 5)
def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 8000):

# After (Configurable)
from agent_labs.config import get_config

def __init__(self, model: Optional[str] = None, max_tokens: int = 8000):
    config = get_config()
    self.model = model or config.provider_config.model
```

### Phase 4: Documentation (Low Priority)

**Files to Create/Update**:
1. `.env.example` - Complete configuration reference
2. `docs/configuration.md` - Configuration guide
3. `README.md` - Update setup instructions
4. Lab READMEs - Document config requirements

---

## Environment Variables Reference

### Required for Production

```bash
# Provider Selection (required)
LLM_PROVIDER=openai  # or: ollama, anthropic, google, azure-openai, mock

# Provider-Specific Model (required)
OPENAI_MODEL=gpt-4
# or
OLLAMA_MODEL=llama2
# or
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# API Authentication (required for cloud)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
AZURE_OPENAI_API_KEY=...
```

### Optional Overrides

```bash
# Base URLs (optional, defaults provided)
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Timeouts (optional)
OLLAMA_TIMEOUT=60
OPENAI_TIMEOUT=30
AGENT_TIMEOUT=300
TOOL_TIMEOUT=30

# Generation Parameters (optional)
OLLAMA_TEMPERATURE=0.7
OPENAI_TEMPERATURE=0.7
TOOL_TEMPERATURE=0.3

# Agent Behavior (optional)
AGENT_MAX_TURNS=10
```

### Testing/CI Configuration

```bash
# CI/CD: Use mock provider
LLM_PROVIDER=mock
MOCK_MODEL=mock-gpt-4

# Local Testing: Use Ollama
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Security Considerations

### ✅ Best Practices

1. **Never commit credentials**: Use environment variables only
2. **Use .env files locally**: Add `.env` to `.gitignore`
3. **Document in .env.example**: Show structure, not secrets
4. **Validate on startup**: Fail fast with clear errors
5. **Log sanitization**: Never log API keys

### 🔒 Secrets Management

**Development**:
```bash
# .env (gitignored)
OPENAI_API_KEY=sk-proj-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

**Production**:
- Use secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- Inject via environment at runtime
- Rotate credentials regularly

---

## Testing Strategy

### Unit Tests

```python
# tests/test_config.py
def test_config_mock_provider():
    os.environ["LLM_PROVIDER"] = "mock"
    config = reload_config()
    assert config.provider == LLMProvider.MOCK
    assert config.provider_config.model == "mock-model"

def test_config_requires_api_key_for_openai():
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_MODEL"] = "gpt-4"
    # No API key set
    config = AgentConfig()
    valid, error = config.validate()
    assert not valid
    assert "API key required" in error
```

### Integration Tests

```python
# tests/integration/test_provider_config.py
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No API key")
def test_openai_provider_from_config():
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
    
    config = get_config()
    provider = create_provider(config.provider, config.provider_config)
    
    response = provider.generate("Hello")
    assert response.text
```

---

## Implementation Checklist

### Core Changes
- [ ] Enhance `src/agent_labs/config.py` with ProviderConfig
- [ ] Add provider factory in `src/agent_labs/llm_providers/__init__.py`
- [ ] Create `.env.example` with all variables documented
- [ ] Add validation to AgentConfig.validate()

### Script Updates
- [ ] Update `scripts/interactive_agent.py` line 57
- [ ] Update `scripts/advanced_interactive_agent.py` line 259
- [ ] Test both scripts with mock/ollama/openai providers

### Lab Updates
- [ ] Fix `labs/05/src/context_agent.py` constructor
- [ ] Update `labs/05/tests/test_context_agent.py` assertions
- [ ] Fix `labs/00/src/hello_agent.py` provider init
- [ ] Fix `labs/01/src/rag_eval.py` provider init

### Testing
- [ ] Add config validation tests
- [ ] Add provider factory tests
- [ ] Test with all supported providers
- [ ] Verify CI/CD with mock provider

### Documentation
- [ ] Create `docs/configuration.md`
- [ ] Update main README.md
- [ ] Update lab READMEs
- [ ] Document security best practices

---

## Breaking Changes

### API Changes

**Old**:
```python
agent = ContextAgent(model="gpt-3.5-turbo")
provider = OllamaProvider(model="llama2", base_url="http://localhost:11434")
```

**New**:
```python
from agent_labs.config import get_config

config = get_config()  # Reads from environment
agent = ContextAgent()  # Uses config automatically
provider = create_provider(config.provider, config.provider_config)
```

### Migration Guide for Users

1. **Copy .env.example to .env**
2. **Set LLM_PROVIDER** (required)
3. **Set provider-specific MODEL** (required)
4. **Set API_KEY** (if using cloud provider)
5. **Test with `python scripts/interactive_agent.py`**

---

## Timeline

- **Phase 1** (Core): 2-3 hours
- **Phase 2** (Scripts): 1-2 hours
- **Phase 3** (Labs): 2-3 hours
- **Phase 4** (Docs): 1-2 hours

**Total Estimate**: 6-10 hours

---

## Conclusion

The current hardcoded configuration violates clean architecture principles and creates technical debt. The proposed unified configuration system:

✅ Eliminates hardcoded values  
✅ Supports multiple providers (Ollama, OpenAI, Anthropic, etc.)  
✅ Follows 12-factor app principles  
✅ Enables secure credential management  
✅ Improves testability with mock providers  
✅ Maintains backwards compatibility (with deprecation warnings)

**Recommendation**: Implement in phases starting with Phase 1 (core infrastructure) to unblock cloud provider integration and improve maintainability.
