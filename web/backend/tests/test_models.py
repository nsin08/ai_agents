"""Tests for models."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from models import ChatRequest, ChatResponse, ErrorResponse


def test_chat_request_valid():
    """Test valid chat request."""
    req = ChatRequest(message="Hello")
    assert req.message == "Hello"
    assert req.provider == "mock"
    assert req.model == "mock-model"


def test_chat_request_empty_message():
    """Test chat request with empty message fails validation."""
    with pytest.raises(ValueError):
        ChatRequest(message="")


def test_chat_request_with_config():
    """Test chat request with custom config."""
    req = ChatRequest(
        message="Test",
        provider="ollama",
        model="llama2",
        config={"temperature": 0.7},
    )
    assert req.provider == "ollama"
    assert req.config["temperature"] == 0.7


def test_chat_response_success():
    """Test successful chat response."""
    resp = ChatResponse(
        success=True,
        response="Hello!",
        metadata={"provider": "mock"},
    )
    assert resp.success is True
    assert resp.response == "Hello!"


def test_chat_response_error():
    """Test error response."""
    resp = ChatResponse(
        success=False,
        response="Error occurred",
    )
    assert resp.success is False


def test_error_response():
    """Test error response model."""
    err = ErrorResponse(error="Test error")
    assert err.success is False
    assert err.error == "Test error"


def test_error_response_with_detail():
    """Test error response with detail."""
    err = ErrorResponse(
        error="Test error",
        detail="More information",
    )
    assert err.error == "Test error"
    assert err.detail == "More information"
