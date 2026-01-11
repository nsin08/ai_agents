"""
Safety Validator Module - Enforce guardrails on agent behavior

This module provides guardrail enforcement for AI agents, including:
- Token budget limits (per-request and per-session)
- Tool allowlists and blocklists
- Output content filtering (PII, profanity)
- Response time constraints
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class GuardrailConfig:
    """Configuration for agent guardrails and safety constraints"""
    
    # Token limits
    max_tokens_per_request: int = 2000
    max_tokens_per_session: int = 20000
    cost_limit_usd: float = 1.0
    
    # Tool constraints
    allowed_tools: Optional[List[str]] = None
    blocked_tools: Optional[List[str]] = None
    
    # Output filtering
    block_pii: bool = True
    block_profanity: bool = False
    max_output_length: int = 1000
    
    # Timing
    max_response_time_sec: float = 5.0
    
    # Environment
    environment: str = "development"  # development | production


class GuardrailViolation(Exception):
    """Raised when a guardrail constraint is violated"""
    
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(f"Guardrail '{rule}' violated: {message}")


class SafetyValidator:
    """Enforce guardrails on agent behavior throughout request lifecycle"""
    
    def __init__(self, config: GuardrailConfig):
        """
        Initialize validator with guardrail configuration
        
        Args:
            config: GuardrailConfig instance defining constraints
        """
        self.config = config
        self.session_tokens = 0
        self.session_cost = 0.0
        self.violations: List[Dict[str, Any]] = []
        self.profanity_list = self._load_profanity_list()
    
    def validate_request(self, query: str) -> None:
        """
        Pre-execution validation of user request
        
        Args:
            query: User query string
            
        Raises:
            GuardrailViolation: If request violates token limits
        """
        # Estimate token count (simple heuristic: ~4 chars per token)
        token_count = len(query) // 4 + 1
        
        # Check per-request token limit
        if token_count > self.config.max_tokens_per_request:
            raise GuardrailViolation(
                "max_tokens_per_request",
                f"Request has {token_count} tokens (limit: {self.config.max_tokens_per_request})"
            )
        
        # Check session token limit
        if self.session_tokens + token_count > self.config.max_tokens_per_session:
            raise GuardrailViolation(
                "max_tokens_per_session",
                f"Session would exceed {self.config.max_tokens_per_session} tokens "
                f"(current: {self.session_tokens}, request: {token_count})"
            )
        
        self.session_tokens += token_count
    
    def validate_tool_call(self, tool_name: str) -> None:
        """
        Validate tool call against allowlist/blocklist
        
        Args:
            tool_name: Name of tool being called
            
        Raises:
            GuardrailViolation: If tool not in allowlist or in blocklist
        """
        # Check allowlist (if specified)
        if self.config.allowed_tools and tool_name not in self.config.allowed_tools:
            raise GuardrailViolation(
                "allowed_tools",
                f"Tool '{tool_name}' not in allowlist: {self.config.allowed_tools}"
            )
        
        # Check blocklist (if specified)
        if self.config.blocked_tools and tool_name in self.config.blocked_tools:
            raise GuardrailViolation(
                "blocked_tools",
                f"Tool '{tool_name}' is blocked: {self.config.blocked_tools}"
            )
    
    def validate_output(self, output: str) -> str:
        """
        Post-execution filtering and validation of agent output
        
        Args:
            output: Raw agent output string
            
        Returns:
            Filtered output that complies with guardrails
        """
        filtered = output
        
        # PII filtering (redact sensitive information)
        if self.config.block_pii:
            filtered = self._redact_pii(filtered)
        
        # Profanity filtering
        if self.config.block_profanity:
            filtered = self._filter_profanity(filtered)
        
        # Length limit (truncate if exceeds max)
        if len(filtered) > self.config.max_output_length:
            filtered = filtered[:self.config.max_output_length] + " ... [truncated]"
        
        return filtered
    
    def _redact_pii(self, text: str) -> str:
        """
        Redact personally identifiable information from text
        
        Patterns redacted:
        - US Social Security Numbers (XXX-XX-XXXX)
        - Credit card numbers (XXXX-XXXX-XXXX-XXXX)
        - Email addresses
        
        Args:
            text: Input text potentially containing PII
            
        Returns:
            Text with PII redacted
        """
        # Social Security Number pattern
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN_REDACTED]',
            text
        )
        
        # Credit card pattern (variations)
        text = re.sub(
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            '[CC_REDACTED]',
            text
        )
        
        # Email pattern
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_REDACTED]',
            text
        )
        
        return text
    
    def _filter_profanity(self, text: str) -> str:
        """
        Replace profanity with [FILTERED]
        
        Args:
            text: Input text potentially containing profanity
            
        Returns:
            Text with profanity filtered
        """
        for word in self.profanity_list:
            text = re.sub(
                rf'\b{word}\b',
                '[FILTERED]',
                text,
                flags=re.IGNORECASE
            )
        return text
    
    def _load_profanity_list(self) -> List[str]:
        """Load profanity list from configuration"""
        # Minimal demo list; in production load from external source
        return [
            # Empty for now - can be configured per environment
        ]
    
    def log_violation(self, violation: GuardrailViolation) -> None:
        """
        Record guardrail violation for monitoring and auditing
        
        Args:
            violation: GuardrailViolation instance
        """
        violation_record = {
            "rule": violation.rule,
            "message": violation.message,
            "timestamp": datetime.now().isoformat(),
            "environment": self.config.environment
        }
        self.violations.append(violation_record)
    
    def get_violation_report(self) -> Dict[str, Any]:
        """
        Get summary report of all violations in this session
        
        Returns:
            Dictionary with violation statistics and list
        """
        return {
            "total_violations": len(self.violations),
            "by_rule": self._group_violations_by_rule(),
            "violations": self.violations,
            "session_tokens": self.session_tokens,
            "session_cost": self.session_cost
        }
    
    def _group_violations_by_rule(self) -> Dict[str, int]:
        """Group violations by rule name"""
        grouped = {}
        for violation in self.violations:
            rule = violation["rule"]
            grouped[rule] = grouped.get(rule, 0) + 1
        return grouped
    
    def reset_session(self) -> None:
        """Reset session counters and violation history"""
        self.session_tokens = 0
        self.session_cost = 0.0
        self.violations = []
