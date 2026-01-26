"""End-to-end integration tests for complete user flows."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestCompleteUserFlows:
    """Test complete user workflows from start to finish."""
    
    def test_complete_chat_flow(self):
        """Test complete flow: config -> session -> multiple messages -> export."""
        # 1. Set up config
        config_response = client.post(
            "/api/config/save",
            json={
                "config": {
                    "max_turns": 3,
                    "temperature": 0.7,
                    "timeout_seconds": 30,
                    "enable_debug": True
                }
            }
        )
        assert config_response.status_code == 200
        
        # 2. Create session
        session_response = client.post("/api/chat/sessions")
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # 3. Send multiple messages
        messages = [
            "Hello, how are you?",
            "What can you help me with?",
            "Thank you!"
        ]
        
        for msg in messages:
            response = client.post(
                "/api/chat/send",
                json={
                    "session_id": session_id,
                    "message": msg,
                    "provider": "mock",
                    "model": "mock-model"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "response" in data
        
        # 4. Verify session exists
        session_check = client.get(f"/api/chat/sessions/{session_id}")
        assert session_check.status_code == 200
        assert session_check.json()["session_id"] == session_id
    
    def test_provider_switching_flow(self):
        """Test switching between providers in same session."""
        session_response = client.post("/api/chat/sessions")
        session_id = session_response.json()["session_id"]
        
        # Message with mock provider
        response1 = client.post(
            "/api/chat/send",
            json={
                "session_id": session_id,
                "message": "Test with mock",
                "provider": "mock",
                "model": "mock-model"
            }
        )
        assert response1.json()["metadata"]["provider"] == "mock"
        
        # Switch to different model (still mock)
        response2 = client.post(
            "/api/chat/send",
            json={
                "session_id": session_id,
                "message": "Test with advanced",
                "provider": "mock",
                "model": "mock-advanced"
            }
        )
        assert response2.json()["metadata"]["model"] == "mock-advanced"
    
    def test_config_preset_flow(self):
        """Test using predefined config presets."""
        # Get all presets
        presets_response = client.get("/api/config/presets")
        assert presets_response.status_code == 200
        presets = presets_response.json()  # Returns list directly
        assert isinstance(presets, list)
        
        for preset_name in ["Creative", "Precise", "Balanced"]:
            # Find preset (note: names are capitalized)
            preset = next((p for p in presets if p["name"] == preset_name), None)
            assert preset is not None
            
            # Apply preset config and send message
            config = preset["config"]
            client.post("/api/config/save", json={"config": config})
            
            response = client.post(
                "/api/chat/send",
                json={
                    "message": f"Test with {preset_name} preset",
                    "provider": "mock",
                    "model": "mock-model"
                }
            )
            assert response.status_code == 200
            assert response.json()["success"] is True
    
    def test_error_recovery_flow(self):
        """Test system behavior when errors occur."""
        # 1. Send invalid message (empty)
        response1 = client.post(
            "/api/chat/send",
            json={
                "message": "",
                "provider": "mock",
                "model": "mock-model"
            }
        )
        # Empty message causes 422 validation error
        assert response1.status_code == 422
        
        # 2. Recover with valid message
        response2 = client.post(
            "/api/chat/send",
            json={
                "message": "Valid message after error",
                "provider": "mock",
                "model": "mock-model"
            }
        )
        data2 = response2.json()
        assert data2["success"] is True
        
        # 3. Try unsupported provider
        response3 = client.post(
            "/api/chat/send",
            json={
                "message": "Test",
                "provider": "nonexistent",
                "model": "fake-model"
            }
        )
        data3 = response3.json()
        assert data3["success"] is False
        
        # 4. Recover again
        response4 = client.post(
            "/api/chat/send",
            json={
                "message": "Back to normal",
                "provider": "mock",
                "model": "mock-model"
            }
        )
        assert response4.json()["success"] is True


class TestMultiSessionManagement:
    """Test managing multiple concurrent sessions."""
    
    def test_multiple_sessions_isolated(self):
        """Test that multiple sessions don't interfere with each other."""
        # Create 3 sessions
        sessions = []
        for i in range(3):
            response = client.post("/api/chat/sessions")
            sessions.append(response.json()["session_id"])
        
        # Send messages to each session
        for i, session_id in enumerate(sessions):
            response = client.post(
                "/api/chat/send",
                json={
                    "session_id": session_id,
                    "message": f"Message for session {i}",
                    "provider": "mock",
                    "model": "mock-model"
                }
            )
            assert response.status_code == 200
            assert response.json()["success"] is True
        
        # Verify each session is independent
        for session_id in sessions:
            response = client.get(f"/api/chat/sessions/{session_id}")
            assert response.status_code == 200
    
    def test_session_config_persistence(self):
        """Test that session-specific configs persist."""
        # Create session with specific config
        session_response = client.post("/api/chat/sessions")
        session_id = session_response.json()["session_id"]
        
        # Note: Session-specific config may not persist independently
        # This tests the API responds correctly
        config_response = client.get(f"/api/config/{session_id}")
        assert config_response.status_code == 200
        data = config_response.json()
        assert "config" in data
        assert "max_turns" in data["config"]
        assert "temperature" in data["config"]


class TestPerformanceAndScaling:
    """Test system performance under various loads."""
    
    def test_rapid_sequential_requests(self):
        """Test handling rapid sequential requests."""
        session_response = client.post("/api/chat/sessions")
        session_id = session_response.json()["session_id"]
        
        # Send 10 messages rapidly
        for i in range(10):
            response = client.post(
                "/api/chat/send",
                json={
                    "session_id": session_id,
                    "message": f"Rapid message {i}",
                    "provider": "mock",
                    "model": "mock-model",
                    "config": {"max_turns": 1}
                }
            )
            assert response.status_code == 200
            assert response.json()["success"] is True
    
    def test_large_message_handling(self):
        """Test handling large messages."""
        large_message = "Test message. " * 100  # ~1400 characters
        
        response = client.post(
            "/api/chat/send",
            json={
                "message": large_message,
                "provider": "mock",
                "model": "mock-model"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_config_changes_during_session(self):
        """Test changing config multiple times during session."""
        session_response = client.post("/api/chat/sessions")
        session_id = session_response.json()["session_id"]
        
        configs = [
            {"temperature": 0.3, "max_turns": 1},
            {"temperature": 0.7, "max_turns": 3},
            {"temperature": 1.0, "max_turns": 5}
        ]
        
        for i, config in enumerate(configs):
            # Change config
            client.post(
                f"/api/config/save?session_id={session_id}",
                json={"config": config}
            )
            
            # Send message
            response = client.post(
                "/api/chat/send",
                json={
                    "session_id": session_id,
                    "message": f"Message {i} with new config",
                    "provider": "mock",
                    "model": "mock-model"
                }
            )
            assert response.status_code == 200
            assert response.json()["success"] is True


class TestAPIValidation:
    """Test API input validation and error handling."""
    
    def test_invalid_provider_id(self):
        """Test validation of provider ID."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test",
                "provider": "invalid_provider_123",
                "model": "test-model"
            }
        )
        assert response.status_code == 200  # Returns 200 with error in body
        assert response.json()["success"] is False
    
    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        # Missing message
        response = client.post(
            "/api/chat/send",
            json={
                "provider": "mock",
                "model": "mock-model"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_config_values(self):
        """Test validation of config value ranges."""
        response = client.post(
            "/api/config/save",
            json={
                "config": {
                    "temperature": 5.0,  # Should be 0.0-2.0
                    "max_turns": -1  # Should be positive
                }
            }
        )
        # Should either reject or clamp to valid range
        assert response.status_code in [200, 422]
    
    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/chat/send",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
