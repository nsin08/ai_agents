"""
Safe Agent Module - Agent with guardrail enforcement

Implements an agent wrapper that integrates SafetyValidator to enforce
guardrails throughout the agent lifecycle: pre-execution validation,
tool call filtering, and post-execution output filtering.
"""

from typing import Dict, Any, Optional, List
import asyncio
from dataclasses import dataclass

from safety_validator import GuardrailConfig, GuardrailViolation, SafetyValidator


@dataclass
class AgentResponse:
    """Response from safe agent with metadata"""
    success: bool
    content: str
    violations: List[Dict[str, Any]]
    tokens_used: int
    metadata: Dict[str, Any]


class SafeAgent:
    """
    Agent with integrated guardrail enforcement
    
    Wraps agent orchestration with safety validation at key points:
    1. Pre-execution: Validate request against token/cost limits
    2. Tool execution: Block disallowed tools
    3. Post-execution: Filter output (PII, profanity, length)
    """
    
    def __init__(
        self,
        guardrail_config: GuardrailConfig,
        orchestrator=None  # Injected agent orchestrator
    ):
        """
        Initialize safe agent with guardrails
        
        Args:
            guardrail_config: GuardrailConfig instance
            orchestrator: Agent orchestrator to wrap (mocked in tests)
        """
        self.config = guardrail_config
        self.validator = SafetyValidator(guardrail_config)
        self.orchestrator = orchestrator
        self.conversation_history: List[Dict[str, str]] = []
    
    async def run(
        self,
        query: str,
        max_turns: int = 3,
        tools: Optional[List[str]] = None
    ) -> AgentResponse:
        """
        Execute agent with guardrail enforcement
        
        Args:
            query: User query/prompt
            max_turns: Maximum reasoning loops
            tools: Available tools (for validation)
            
        Returns:
            AgentResponse with success status, content, and violation info
        """
        try:
            # Step 1: Pre-execution validation
            self.validator.validate_request(query)
            
            # Step 2: Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })
            
            # Step 3: Execute agent (mocked or real orchestrator)
            if self.orchestrator:
                result = await self._run_orchestrator(query, max_turns, tools)
            else:
                result = await self._run_mock_agent(query)
            
            # Step 4: Post-execution output filtering
            filtered_result = self.validator.validate_output(result)
            
            # Step 5: Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": filtered_result
            })
            
            return AgentResponse(
                success=True,
                content=filtered_result,
                violations=self.validator.violations,
                tokens_used=self.validator.session_tokens,
                metadata={
                    "turns": 1,
                    "tools_called": [],
                    "cost": self.validator.session_cost
                }
            )
        
        except GuardrailViolation as e:
            # Log violation and return error response
            self.validator.log_violation(e)
            
            error_message = f"Request blocked by guardrail '{e.rule}': {e.message}"
            
            return AgentResponse(
                success=False,
                content=error_message,
                violations=[{
                    "rule": e.rule,
                    "message": e.message,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }],
                tokens_used=self.validator.session_tokens,
                metadata={
                    "blocked_by": e.rule,
                    "error": e.message
                }
            )
        
        except Exception as e:
            # Unexpected error
            return AgentResponse(
                success=False,
                content=f"Unexpected error: {str(e)}",
                violations=self.validator.violations,
                tokens_used=self.validator.session_tokens,
                metadata={"error_type": type(e).__name__}
            )
    
    def validate_tool_call(self, tool_name: str) -> None:
        """
        Validate that agent can call a specific tool
        
        Args:
            tool_name: Name of tool
            
        Raises:
            GuardrailViolation: If tool not allowed
        """
        try:
            self.validator.validate_tool_call(tool_name)
        except GuardrailViolation as e:
            self.validator.log_violation(e)
            raise
    
    async def _run_orchestrator(
        self,
        query: str,
        max_turns: int,
        tools: Optional[List[str]]
    ) -> str:
        """
        Run real orchestrator (if available)
        
        Args:
            query: User query
            max_turns: Max reasoning turns
            tools: Available tools
            
        Returns:
            Agent response string
        """
        # Validate tools if provided
        if tools:
            for tool in tools:
                self.validate_tool_call(tool)
        
        # In real implementation, call self.orchestrator.run(query, max_turns=max_turns)
        # For now, return mock response
        return f"Orchestrator response to: {query[:50]}..."
    
    async def _run_mock_agent(self, query: str) -> str:
        """
        Run mock agent (for testing without orchestrator)
        
        Args:
            query: User query
            
        Returns:
            Mock agent response
        """
        await asyncio.sleep(0.1)  # Simulate processing
        return f"Mock response to: {query}"
    
    def reset(self) -> None:
        """Reset agent session state"""
        self.validator.reset_session()
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def get_violation_report(self) -> Dict[str, Any]:
        """Get guardrail violation report"""
        return self.validator.get_violation_report()
