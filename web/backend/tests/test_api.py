"""Tests for backend API."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Agent Chat API"


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_send_message_success():
    """Test sending a message successfully."""
    response = client.post(
        "/api/chat/send",
        json={
            "message": "What is Python?",
            "provider": "mock",
            "model": "mock-model",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "response" in data
    assert data["metadata"]["provider"] == "mock"


def test_send_message_unsupported_provider():
    """Test unsupported provider returns error."""
    response = client.post(
        "/api/chat/send",
        json={
            "message": "Test",
            "provider": "unsupported",
            "model": "mock-model",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Unknown provider" in data["response"] or "Invalid provider" in data["response"]


def test_send_message_empty():
    """Test sending empty message."""
    response = client.post(
        "/api/chat/send",
        json={
            "message": "",
            "provider": "mock",
            "model": "mock-model",
        },
    )
    assert response.status_code == 422  # Validation error


def test_create_session():
    """Test creating a new session."""
    response = client.post("/api/chat/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data


def test_get_session():
    """Test retrieving session."""
    # Create session first
    create_response = client.post("/api/chat/sessions")
    session_id = create_response.json()["session_id"]

    # Get session
    response = client.get(f"/api/chat/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_send_message_async():
    """Test async message processing."""
    response = client.post(
        "/api/chat/send",
        json={
            "message": "Test message",
            "provider": "mock",
            "model": "mock-model",
            "config": {"max_turns": 1},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["metadata"]["max_turns"] == 1
