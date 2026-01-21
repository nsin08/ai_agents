"""Request/Response models for API."""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    provider: str = Field(default="mock", description="LLM provider to use")
    model: str = Field(default="mock-model", description="Model name")
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
