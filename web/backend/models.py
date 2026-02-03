"""Request/Response models for API."""
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ProviderEnum(str, Enum):
    """Available LLM providers."""
    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure-openai"


class ProviderInfo(BaseModel):
    """Information about a provider."""
    id: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Display name")
    requires_api_key: bool = Field(..., description="Whether API key is required")
    supported_models: list[str] = Field(default_factory=list, description="Available models")
    api_key_env_var: Optional[str] = Field(None, description="Environment variable for API key")
    status: str = Field(default="available", description="Provider status: available, coming_soon, deprecated")


class ProviderRequest(BaseModel):
    """Request to get available providers."""
    include_models: bool = Field(default=False, description="Include model list")


class ValidateKeyRequest(BaseModel):
    """Request to validate an API key."""
    provider: ProviderEnum = Field(..., description="Provider to validate")
    api_key: str = Field(..., min_length=1, description="API key to validate")
    model: Optional[str] = Field(None, description="Specific model to test")


class ValidateKeyResponse(BaseModel):
    """Response from API key validation."""
    valid: bool = Field(..., description="Whether key is valid")
    message: str = Field(..., description="Validation message")
    models_available: Optional[list[str]] = Field(None, description="Available models if valid")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    provider: str = Field(default="mock", description="LLM provider to use")
    model: str = Field(default="mock-model", description="Model name")
    api_key: Optional[str] = Field(None, description="Optional API key (overrides env var)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent config")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    success: bool = Field(..., description="Whether request succeeded")
    response: str = Field(..., description="Agent response text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Basic metadata")
    debug_metadata: Optional[Dict[str, Any]] = Field(None, description="Debug metadata (only when debug mode enabled)")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")


# Phase 3: Debug & Configuration Models

class DebugMetadata(BaseModel):
    """Debug metadata for chat responses."""
    tokens_used: Optional[int] = Field(None, description="Total tokens used")
    tokens_input: Optional[int] = Field(None, description="Input tokens")
    tokens_output: Optional[int] = Field(None, description="Output tokens")
    latency_ms: float = Field(..., description="Response time in milliseconds")
    provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model name used")
    max_turns: int = Field(default=3, description="Maximum turns allowed")
    current_turn: int = Field(default=1, description="Current turn number")
    temperature: float = Field(default=0.7, description="Temperature setting")
    agent_state: Optional[str] = Field(None, description="Agent state (Observe/Plan/Act/Verify)")
    reasoning: Optional[str] = Field(None, description="Agent reasoning chain")
    tool_calls: Optional[list[str]] = Field(None, description="Tools used by agent")
    errors: Optional[list[str]] = Field(None, description="Errors encountered")
    backend: str = Field(default="agent_labs", description="Backend implementation")


class AgentConfig(BaseModel):
    """Agent configuration settings."""
    max_turns: int = Field(default=1, ge=1, le=10, description="Max iterations (1-10)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature (0.0-2.0)")
    timeout_seconds: int = Field(default=90, ge=5, le=300, description="Timeout in seconds")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    enable_debug: bool = Field(default=False, description="Enable debug mode")


class ConfigRequest(BaseModel):
    """Request to save configuration."""
    config: AgentConfig = Field(..., description="Configuration to save")
    preset: Optional[str] = Field(None, description="Preset name (creative, precise, balanced)")
    session_id: Optional[str] = Field(None, description="Session ID for session-specific config")


class ConfigResponse(BaseModel):
    """Response with configuration."""
    success: bool = Field(..., description="Whether operation succeeded")
    config: AgentConfig = Field(..., description="Current configuration")
    message: Optional[str] = Field(None, description="Status message")


class PresetConfig(BaseModel):
    """Preset configuration template."""
    name: str = Field(..., description="Preset name")
    description: str = Field(..., description="Description")
    config: AgentConfig = Field(..., description="Configuration")
