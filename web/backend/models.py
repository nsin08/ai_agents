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
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Debug metadata")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
