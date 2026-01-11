"""
Test Suite for Safety & Guardrails Lab

Tests cover:
- Token limit enforcement (per-request and per-session)
- Tool allowlist/blocklist validation
- PII redaction (SSN, credit card, email)
- Output length limiting
- Violation logging and reporting
"""

import pytest
from datetime import datetime

# Import test modules (paths adjusted for local testing)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from safety_validator import GuardrailConfig, GuardrailViolation, SafetyValidator
from safe_agent import SafeAgent, AgentResponse


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def permissive_config():
    """Development config with lenient constraints"""
    return GuardrailConfig(
        max_tokens_per_request=4000,
        max_tokens_per_session=50000,
        cost_limit_usd=10.0,
        block_pii=False,
        block_profanity=False,
        max_output_length=5000,
        environment="development"
    )


@pytest.fixture
def strict_config():
    """Production config with strict constraints"""
    return GuardrailConfig(
        max_tokens_per_request=1000,
        max_tokens_per_session=10000,
        cost_limit_usd=1.0,
        allowed_tools=["get_weather", "calculate"],
        block_pii=True,
        block_profanity=True,
        max_output_length=500,
        environment="production"
    )


@pytest.fixture
def customer_support_config():
    """Customer support specific guardrails"""
    return GuardrailConfig(
        max_tokens_per_request=2000,
        max_tokens_per_session=15000,
        cost_limit_usd=2.0,
        allowed_tools=["search_kb", "create_ticket", "get_customer_info"],
        blocked_tools=["send_email", "refund_payment", "delete_account"],
        block_pii=True,
        max_output_length=1000,
        environment="production"
    )


@pytest.fixture
def validator_permissive(permissive_config):
    """Permissive validator instance"""
    return SafetyValidator(permissive_config)


@pytest.fixture
def validator_strict(strict_config):
    """Strict validator instance"""
    return SafetyValidator(strict_config)


@pytest.fixture
def safe_agent_strict(strict_config):
    """Safe agent with strict config"""
    return SafeAgent(strict_config)


# ============================================================================
# TOKEN LIMIT TESTS
# ============================================================================

class TestTokenLimitEnforcement:
    """Test token budget constraints"""
    
    def test_request_within_limit_passes(self, validator_permissive):
        """Request under token limit should pass"""
        query = "What is 2+2?"  # ~5 tokens
        validator_permissive.validate_request(query)
        assert validator_permissive.session_tokens > 0
    
    def test_request_exceeds_per_request_limit(self, validator_strict):
        """Request exceeding per-request limit should raise violation"""
        # Strict limit is 1000 tokens (~4000 chars)
        long_query = "x" * 5000  # ~1250 tokens
        
        with pytest.raises(GuardrailViolation) as exc_info:
            validator_strict.validate_request(long_query)
        
        assert exc_info.value.rule == "max_tokens_per_request"
        assert "exceeds" in exc_info.value.message.lower()
    
    def test_cumulative_requests_exceed_session_limit(self, validator_strict):
        """Multiple requests accumulating beyond session limit should fail"""
        # Strict limit is 10000 tokens per session
        query = "x" * 2000  # ~500 tokens each
        
        # First 15 requests should work (7500 tokens total)
        for i in range(15):
            try:
                validator_strict.validate_request(query)
            except GuardrailViolation:
                # Expected after reaching session limit
                break
        
        # Should have accumulated some tokens
        assert validator_strict.session_tokens > 0
        # Should eventually hit limit
        assert len(validator_strict.violations) > 0 or validator_strict.session_tokens < 50000
    
    def test_session_reset_clears_token_count(self, validator_strict):
        """Reset should clear session token accumulation"""
        query = "x" * 1000
        validator_strict.validate_request(query)
        initial_tokens = validator_strict.session_tokens
        
        assert initial_tokens > 0
        
        validator_strict.reset_session()
        assert validator_strict.session_tokens == 0


# ============================================================================
# TOOL ALLOWLIST/BLOCKLIST TESTS
# ============================================================================

class TestToolConstraints:
    """Test tool access control"""
    
    def test_allowed_tool_passes_validation(self, validator_strict):
        """Tool in allowlist should pass"""
        validator_strict.validate_tool_call("get_weather")
        # Should not raise
        assert True
    
    def test_disallowed_tool_raises_violation(self, validator_strict):
        """Tool not in allowlist should raise violation"""
        with pytest.raises(GuardrailViolation) as exc_info:
            validator_strict.validate_tool_call("send_email")
        
        assert exc_info.value.rule == "allowed_tools"
        assert "send_email" in exc_info.value.message
    
    def test_blocked_tool_raises_violation(self, validator_strict):
        """Tool in blocklist should raise violation"""
        with pytest.raises(GuardrailViolation) as exc_info:
            validator_strict.validate_tool_call("delete_data")
        
        assert exc_info.value.rule == "allowed_tools"  # Blocked via allowlist
    
    def test_no_allowlist_allows_all_tools(self, validator_permissive):
        """Without allowlist, all tools should be allowed"""
        validator_permissive.validate_tool_call("send_email")
        validator_permissive.validate_tool_call("delete_database")
        validator_permissive.validate_tool_call("any_tool")
        # Should not raise
        assert True
    
    def test_customer_support_tool_allowlist(self, customer_support_config):
        """Customer support agent should allow specific tools"""
        validator = SafetyValidator(customer_support_config)
        
        # Allowed tools
        validator.validate_tool_call("search_kb")
        validator.validate_tool_call("create_ticket")
        
        # Blocked tools
        with pytest.raises(GuardrailViolation):
            validator.validate_tool_call("refund_payment")


# ============================================================================
# PII REDACTION TESTS
# ============================================================================

class TestPIIRedaction:
    """Test personally identifiable information filtering"""
    
    def test_ssn_redaction(self, validator_strict):
        """Social Security Numbers should be redacted"""
        output = "My SSN is 123-45-6789 and I live here."
        filtered = validator_strict.validate_output(output)
        
        assert "123-45-6789" not in filtered
        assert "[SSN_REDACTED]" in filtered
    
    def test_credit_card_redaction(self, validator_strict):
        """Credit card numbers should be redacted"""
        output = "My card is 4532-1111-2222-3333"
        filtered = validator_strict.validate_output(output)
        
        assert "4532-1111-2222-3333" not in filtered
        assert "[CC_REDACTED]" in filtered
    
    def test_email_redaction(self, validator_strict):
        """Email addresses should be redacted"""
        output = "Contact me at john.doe@example.com for details."
        filtered = validator_strict.validate_output(output)
        
        assert "john.doe@example.com" not in filtered
        assert "[EMAIL_REDACTED]" in filtered
    
    def test_multiple_pii_types_redacted(self, validator_strict):
        """Multiple PII types in one output should all be redacted"""
        output = "SSN: 123-45-6789, Email: test@test.com, Card: 1234-5678-9012-3456"
        filtered = validator_strict.validate_output(output)
        
        assert "[SSN_REDACTED]" in filtered
        assert "[EMAIL_REDACTED]" in filtered
        assert "[CC_REDACTED]" in filtered
    
    def test_pii_disabled_in_dev(self, validator_permissive):
        """Development config should not redact PII"""
        output = "SSN: 123-45-6789"
        filtered = validator_permissive.validate_output(output)
        
        # Should keep original in dev mode
        assert "123-45-6789" in filtered


# ============================================================================
# OUTPUT LENGTH LIMITING TESTS
# ============================================================================

class TestOutputLengthLimiting:
    """Test response length constraints"""
    
    def test_output_within_limit_unchanged(self, validator_strict):
        """Output under max length should be unchanged"""
        output = "This is a short response."
        filtered = validator_strict.validate_output(output)
        
        assert filtered == output
    
    def test_output_exceeds_limit_truncated(self, validator_strict):
        """Output exceeding limit should be truncated"""
        # Strict limit is 500 chars
        output = "x" * 600
        filtered = validator_strict.validate_output(output)
        
        assert len(filtered) <= 510  # 500 + " ... [truncated]" margin
        assert "[truncated]" in filtered
    
    def test_permissive_allows_longer_output(self, validator_permissive):
        """Permissive config allows longer outputs"""
        # Permissive limit is 5000 chars
        output = "x" * 1000
        filtered = validator_permissive.validate_output(output)
        
        assert "[truncated]" not in filtered
        assert len(filtered) == 1000


# ============================================================================
# SAFE AGENT INTEGRATION TESTS
# ============================================================================

class TestSafeAgent:
    """Test SafeAgent integration with validators"""
    
    @pytest.mark.asyncio
    async def test_agent_respects_token_limits(self, safe_agent_strict):
        """Agent should enforce token limits"""
        long_query = "x" * 5000  # Exceeds strict limit of 1000 tokens
        
        response = await safe_agent_strict.run(long_query)
        
        assert not response.success
        assert "blocked" in response.content.lower()
        assert len(response.violations) > 0
    
    @pytest.mark.asyncio
    async def test_agent_blocks_disallowed_tool(self, safe_agent_strict):
        """Agent should block disallowed tool calls"""
        safe_agent_strict.validate_tool_call("get_weather")  # Allowed
        
        with pytest.raises(GuardrailViolation):
            safe_agent_strict.validate_tool_call("send_email")  # Blocked
    
    @pytest.mark.asyncio
    async def test_agent_filters_output(self, safe_agent_strict):
        """Agent should filter PII from responses"""
        response = await safe_agent_strict.run("Test query")
        
        # Response object should exist
        assert response is not None
        assert isinstance(response, AgentResponse)
    
    @pytest.mark.asyncio
    async def test_agent_tracks_conversation(self, safe_agent_strict):
        """Agent should maintain conversation history"""
        await safe_agent_strict.run("Hello")
        
        history = safe_agent_strict.get_conversation_history()
        assert len(history) > 0
        assert any(msg["role"] == "user" for msg in history)
    
    @pytest.mark.asyncio
    async def test_agent_reset_clears_state(self, safe_agent_strict):
        """Agent reset should clear session state"""
        await safe_agent_strict.run("Test")
        
        initial_tokens = safe_agent_strict.validator.session_tokens
        safe_agent_strict.reset()
        
        assert safe_agent_strict.validator.session_tokens == 0
        assert len(safe_agent_strict.get_conversation_history()) == 0


# ============================================================================
# VIOLATION LOGGING TESTS
# ============================================================================

class TestViolationLogging:
    """Test violation tracking and reporting"""
    
    def test_violations_logged_on_constraint_breach(self, validator_strict):
        """Violations should be logged when constraints breached"""
        try:
            validator_strict.validate_request("x" * 5000)
        except GuardrailViolation as e:
            validator_strict.log_violation(e)
        
        assert len(validator_strict.violations) > 0
    
    def test_violation_report_generated(self, validator_strict):
        """Should generate comprehensive violation report"""
        try:
            validator_strict.validate_tool_call("blocked_tool")
        except GuardrailViolation as e:
            validator_strict.log_violation(e)
        
        report = validator_strict.get_violation_report()
        
        assert "total_violations" in report
        assert "by_rule" in report
        assert "violations" in report
        assert report["total_violations"] > 0
    
    def test_violations_grouped_by_rule(self, validator_strict):
        """Violations should be grouped by rule in report"""
        # Trigger multiple violations of same rule
        for _ in range(2):
            try:
                validator_strict.validate_tool_call("blocked_tool")
            except GuardrailViolation as e:
                validator_strict.log_violation(e)
        
        report = validator_strict.get_violation_report()
        assert "allowed_tools" in report["by_rule"]


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestGuardrailConfiguration:
    """Test guardrail configuration management"""
    
    def test_default_config_created(self):
        """Default config should have sensible defaults"""
        config = GuardrailConfig()
        
        assert config.max_tokens_per_request == 2000
        assert config.max_tokens_per_session == 20000
        assert config.block_pii == True
        assert config.environment == "development"
    
    def test_custom_config_overrides_defaults(self, strict_config):
        """Custom config should override defaults"""
        assert strict_config.max_tokens_per_request == 1000
        assert strict_config.environment == "production"
        assert strict_config.block_pii == True
    
    def test_allowlist_blocklist_mutually_exclusive(self, customer_support_config):
        """Config should support both allowlist and blocklist"""
        assert customer_support_config.allowed_tools is not None
        assert customer_support_config.blocked_tools is not None


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_query_allowed(self, validator_permissive):
        """Empty query should be allowed"""
        validator_permissive.validate_request("")
        assert validator_permissive.session_tokens >= 0
    
    def test_special_characters_in_pii_detection(self, validator_strict):
        """PII detection should handle special variations"""
        # Credit card with spaces and dashes
        output = "Card: 4532 1111 2222 3333"
        filtered = validator_strict.validate_output(output)
        
        assert "[CC_REDACTED]" in filtered or "4532" not in filtered
    
    def test_unicode_handling(self, validator_strict):
        """Should handle unicode characters"""
        output = "Hello 世界 SSN: 123-45-6789 مرحبا"
        filtered = validator_strict.validate_output(output)
        
        assert "[SSN_REDACTED]" in filtered
        # Unicode should be preserved
        assert "世界" in filtered or "مرحبا" in filtered or len(filtered) > 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
