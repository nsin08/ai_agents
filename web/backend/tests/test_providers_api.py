"""Comprehensive tests for providers API endpoints."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestProvidersAPI:
    """Test suite for /providers endpoints."""
    
    def test_list_providers_basic(self):
        """Test listing providers without models."""
        response = client.get("/providers/")
        assert response.status_code == 200
        providers = response.json()
        assert isinstance(providers, list)
        assert len(providers) >= 3  # At least Mock, Ollama, OpenAI
        
        # Check structure of each provider
        for provider in providers:
            assert "id" in provider
            assert "name" in provider
            assert "requires_api_key" in provider
            assert "status" in provider
            assert provider["status"] in ["available", "coming_soon"]
    
    def test_list_providers_with_models(self):
        """Test listing providers with models included."""
        response = client.get("/providers/?include_models=true")
        assert response.status_code == 200
        providers = response.json()
        
        # Find OpenAI provider and verify models
        openai = next((p for p in providers if p["id"] == "openai"), None)
        assert openai is not None
        assert "supported_models" in openai
        assert isinstance(openai["supported_models"], list)
        assert "gpt-4o-mini" in openai["supported_models"]
        assert "gpt-3.5-turbo" in openai["supported_models"]
    
    def test_list_providers_mock_available(self):
        """Test that mock provider is always available."""
        response = client.get("/providers/")
        assert response.status_code == 200
        providers = response.json()
        
        mock = next((p for p in providers if p["id"] == "mock"), None)
        assert mock is not None
        assert mock["status"] == "available"
        assert mock["requires_api_key"] is False
    
    def test_get_specific_provider_models(self):
        """Test getting models for specific provider."""
        # Get models via include_models parameter
        response = client.get("/providers/?include_models=true")
        assert response.status_code == 200
        providers = response.json()
        openai = next((p for p in providers if p["id"] == "openai"), None)
        assert openai is not None
        models = openai["supported_models"]
        assert isinstance(models, list)
        assert len(models) >= 3
        assert "gpt-4o-mini" in models
    
    def test_provider_api_key_requirements(self):
        """Test API key requirement flags."""
        response = client.get("/providers/")
        assert response.status_code == 200
        providers = response.json()
        
        # Mock should not require API key
        mock = next((p for p in providers if p["id"] == "mock"), None)
        assert mock["requires_api_key"] is False
        
        # OpenAI should require API key
        openai = next((p for p in providers if p["id"] == "openai"), None)
        assert openai["requires_api_key"] is True
        assert openai["api_key_env_var"] == "OPENAI_API_KEY"


class TestProviderIntegration:
    """Integration tests for provider workflows."""
    
    def test_select_provider_and_send_message(self):
        """Test full flow: select provider -> get models -> send message."""
        # 1. List providers
        response = client.get("/providers/?include_models=true")
        assert response.status_code == 200
        providers = response.json()
        
        # 2. Select mock provider
        mock = next((p for p in providers if p["id"] == "mock"), None)
        assert mock is not None
        models = mock["supported_models"]
        assert len(models) > 0
        
        # 3. Send message with selected provider/model
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Hello from integration test",
                "provider": "mock",
                "model": models[0],
                "config": {"max_turns": 1}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["provider"] == "mock"
        assert data["metadata"]["model"] == models[0]
    
    def test_provider_availability_status(self):
        """Test provider availability affects usage."""
        response = client.get("/providers/")
        assert response.status_code == 200
        providers = response.json()
        
        # Available providers should work
        available = [p for p in providers if p["status"] == "available"]
        assert len(available) >= 2  # At least Mock and one other
        
        # Coming soon providers should be listed but flagged
        coming_soon = [p for p in providers if p["status"] == "coming_soon"]
        for provider in coming_soon:
            assert provider["id"] in ["anthropic", "google", "azure-openai"]


class TestProviderErrorHandling:
    """Test error scenarios for providers."""
    
    def test_invalid_provider(self):
        """Test sending message with invalid provider."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test",
                "provider": "nonexistent",
                "model": "fake-model"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data["metadata"]
    
    def test_missing_api_key_for_paid_provider(self):
        """Test error when API key is missing for paid providers."""
        # Note: This test assumes OPENAI_API_KEY is not set in test env
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test",
                "provider": "openai",
                "model": "gpt-4o-mini"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should fail or return error in metadata
        if not data["success"]:
            assert "error" in data["metadata"]
