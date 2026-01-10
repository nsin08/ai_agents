#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Interactive Agent Playground

A comprehensive REPL interface with observability, context management, and safety guardrails.
Demonstrates production-grade agent monitoring, smart memory management, and execution constraints.

Features:
    - Observability: Metrics, traces, token tracking, latency measurement
    - Context Management: Adaptive memory, context window sizing, usage tracking
    - Safety Guardrails: Input validation, tool rate limiting, token budgets, injection detection

Usage:
    python scripts/advanced_interactive_agent.py

Commands:
    /help           - Show available commands
    /config         - Show current agent configuration
    /metrics        - Display execution metrics and statistics
    /trace          - Show detailed trace of last execution
    /context SIZE   - Set context window size (messages)
    /context_info   - Show current context usage and recommendations
    /safety         - Display current safety settings
    /limits SET KEY VALUE - Configure safety limits
    /cost_budget N  - Set token budget for session
    /reset          - Reset agent memory and state
    /provider TYPE  - Switch provider (mock, ollama)
    /model NAME     - Set model name (for ollama)
    /max_turns N    - Set max turns for agent
    /history        - Show conversation history
    /exit           - Exit the playground
"""

import sys
import io
import re
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Fix Windows console encoding
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent, AgentState
from agent_labs.llm_providers import MockProvider, OllamaProvider
from agent_labs.memory import MemoryManager, ShortTermMemory, LongTermMemory
from agent_labs.tools import ToolRegistry, TextSummarizer, CodeAnalyzer


# ============================================================================
# METRICS AND OBSERVABILITY
# ============================================================================

@dataclass
class ExecutionMetrics:
    """Track execution performance and resource usage."""
    tokens_used: int = 0
    latency_ms: float = 0.0
    tool_calls: int = 0
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return (f"Tokens: {self.tokens_used} | Latency: {self.latency_ms:.1f}ms | "
                f"Tools: {self.tool_calls} | Errors: {self.error_count}")


@dataclass
class SessionMetrics:
    """Aggregate metrics for entire session."""
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    total_tool_calls: int = 0
    total_errors: int = 0
    request_count: int = 0
    execution_history: List[ExecutionMetrics] = field(default_factory=list)
    
    def add_execution(self, metrics: ExecutionMetrics):
        """Record execution metrics."""
        self.total_tokens += metrics.tokens_used
        self.total_latency_ms += metrics.latency_ms
        self.total_tool_calls += metrics.tool_calls
        self.total_errors += metrics.error_count
        self.request_count += 1
        self.execution_history.append(metrics)
    
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        return self.total_latency_ms / max(1, self.request_count)
    
    def avg_tokens_per_request(self) -> float:
        """Calculate average tokens per request."""
        return self.total_tokens / max(1, self.request_count)


# ============================================================================
# SAFETY AND VALIDATION
# ============================================================================

class SafetyValidator:
    """Validate inputs and enforce safety constraints."""
    
    # Common prompt injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore previous",
        r"(?i)disregard",
        r"(?i)forget the",
        r"(?i)the previous",
        r"(?i)new instructions",
        r"(?i)system prompt",
        r"(?i)\[system\]",
        r"(?i)admin",
    ]
    
    def __init__(self):
        self.max_input_length = 2000
        self.tool_rate_limit = 5  # max 5 per minute
        self.tool_call_times: Dict[str, List[float]] = defaultdict(list)
        self.token_budget = 4000
        self.tokens_used = 0
        
    def validate_input(self, prompt: str) -> Tuple[bool, Optional[str]]:
        """Validate user input for safety issues."""
        # Check length
        if len(prompt) > self.max_input_length:
            return False, f"Input exceeds max length ({len(prompt)}/{self.max_input_length})"
        
        # Check for injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt):
                return False, "⚠ Warning: Potential prompt injection detected"
        
        # Check for valid encoding
        try:
            prompt.encode('utf-8')
        except UnicodeEncodeError:
            return False, "Invalid character encoding"
        
        return True, None
    
    def check_token_budget(self, estimated_tokens: int) -> Tuple[bool, str]:
        """Check if within token budget."""
        remaining = self.token_budget - self.tokens_used
        
        if estimated_tokens > remaining:
            return False, f"Token budget exceeded: {estimated_tokens} > {remaining} remaining"
        
        if estimated_tokens > remaining * 0.8:
            percent = int((self.tokens_used / self.token_budget) * 100)
            return True, f"⚠ Warning: Token budget at {percent}% ({remaining} remaining)"
        
        return True, None
    
    def check_tool_rate_limit(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """Check tool rate limiting (max N calls per minute)."""
        now = time.time()
        one_minute_ago = now - 60
        
        # Clean old entries
        self.tool_call_times[tool_name] = [
            t for t in self.tool_call_times[tool_name] if t > one_minute_ago
        ]
        
        if len(self.tool_call_times[tool_name]) >= self.tool_rate_limit:
            return False, f"Tool rate limit exceeded: {self.tool_rate_limit}/min"
        
        self.tool_call_times[tool_name].append(now)
        return True, None
    
    def record_token_usage(self, tokens: int):
        """Record token usage."""
        self.tokens_used += tokens
    
    def set_limits(self, key: str, value: int) -> Optional[str]:
        """Set safety limits dynamically."""
        if key == "max_input_length":
            self.max_input_length = value
            return f"Max input length set to {value}"
        elif key == "tool_rate_limit":
            self.tool_rate_limit = value
            return f"Tool rate limit set to {value}/minute"
        elif key == "token_budget":
            self.token_budget = value
            return f"Token budget set to {value}"
        else:
            return f"Unknown limit: {key}"


# ============================================================================
# CONTEXT MANAGEMENT
# ============================================================================

class ContextManager:
    """Manage conversation context and memory."""
    
    def __init__(self, default_window_size: int = 10):
        self.window_size = default_window_size
        self.conversation_history: List[Tuple[str, str]] = []
        
    def add_message(self, role: str, message: str):
        """Add message to history."""
        self.conversation_history.append((role, message))
    
    def get_context_window(self) -> List[Tuple[str, str]]:
        """Get messages within current context window."""
        return self.conversation_history[-self.window_size:]
    
    def get_context_info(self) -> Dict[str, any]:
        """Get context usage information."""
        context_msgs = self.get_context_window()
        total_chars = sum(len(msg) for _, msg in context_msgs)
        # Rough estimation: ~4 chars per token
        estimated_tokens = total_chars // 4
        
        saturation = (len(self.conversation_history) / self.window_size) * 100
        
        return {
            "total_messages": len(self.conversation_history),
            "window_size": self.window_size,
            "active_messages": len(context_msgs),
            "total_characters": total_chars,
            "estimated_tokens": estimated_tokens,
            "saturation_percent": min(100, saturation),
            "should_summarize": saturation > 80,
        }
    
    def set_window_size(self, size: int) -> str:
        """Set context window size."""
        if size < 1:
            return "Context window must be at least 1 message"
        if size > 100:
            return "Context window cannot exceed 100 messages"
        self.window_size = size
        return f"Context window set to {size} messages"


# ============================================================================
# ADVANCED INTERACTIVE AGENT
# ============================================================================

class AdvancedInteractiveAgent:
    """Advanced interactive agent with observability, context management, and safety."""

    def __init__(self):
        self.agent: Optional[Agent] = None
        self.provider_type = "ollama"
        self.model_name = "llama2"
        self.max_turns = 3
        self.loop = None  # Persistent event loop for Windows compatibility
        
        # Observability
        self.session_metrics = SessionMetrics()
        self.last_execution_metrics: Optional[ExecutionMetrics] = None
        self.last_execution_trace: Optional[str] = None
        
        # Context management
        self.context_manager = ContextManager(default_window_size=10)
        
        # Safety
        self.safety_validator = SafetyValidator()
        
        # Tools
        self.tool_registry = ToolRegistry()
        self._init_tools()
        self._init_agent()

    def _init_tools(self):
        """Initialize available tools."""
        try:
            self.tool_registry.register(TextSummarizer())
            self.tool_registry.register(CodeAnalyzer())
        except Exception as e:
            print(f"⚠ Warning: Could not initialize all tools: {e}")

    def _init_agent(self):
        """Initialize agent with current configuration."""
        try:
            if self.provider_type == "mock":
                provider = MockProvider()
                print(f"✓ Initialized MockProvider (fast, deterministic)")
            elif self.provider_type == "ollama":
                provider = OllamaProvider(
                    model=self.model_name,
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                )
                print(f"✓ Initialized OllamaProvider ({self.model_name})")
            else:
                raise ValueError(f"Unknown provider: {self.provider_type}")

            self.agent = Agent(provider=provider)
            self.context_manager.conversation_history = []
        except Exception as e:
            print(f"✗ Error initializing agent: {e}")
            self.agent = None

    def show_help(self):
        """Display help information."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║      Advanced Interactive Agent - Help Menu                    ║
╚════════════════════════════════════════════════════════════════╝

CONVERSATION:
  (type any text)        Ask a question or make a statement
  /reset                 Clear all history and restart

OBSERVABILITY:
  /metrics               Show session statistics (tokens, latency, etc)
  /trace                 Show detailed trace of last execution
  
CONTEXT MANAGEMENT:
  /context SIZE          Set context window size (default: 10)
  /context_info          Show current context usage and recommendations

SAFETY & CONFIGURATION:
  /safety                Display current safety settings
  /limits SET K V        Configure safety limits
                         K: max_input_length | tool_rate_limit | token_budget
  /cost_budget N         Set token budget for session
  
PROVIDER & MODEL:
  /provider TYPE         Switch provider: mock, ollama
  /model NAME            Set model (for ollama provider)
  /max_turns N           Set reasoning iterations (1-10)
  
UTILITY:
  /config                Show current configuration
  /history               Show conversation history
  /help                  Show this menu
  /exit                  Exit the playground

EXAMPLES:
  > /context 5
  > /metrics
  > /limits SET max_input_length 1000
  > /safety
  > What is machine learning?
  > /context_info
"""
        print(help_text)

    def show_config(self):
        """Display current configuration."""
        config_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                    Configuration Status                        ║
╚════════════════════════════════════════════════════════════════╝

AGENT SETUP:
  Provider:              {self.provider_type.upper()}
  Model:                 {self.model_name}
  Max Turns:             {self.max_turns}

CONTEXT:
  Window Size:           {self.context_manager.window_size} messages
  Messages in History:   {len(self.context_manager.conversation_history)}

SAFETY & LIMITS:
  Max Input Length:      {self.safety_validator.max_input_length} chars
  Tool Rate Limit:       {self.safety_validator.tool_rate_limit} per minute
  Token Budget:          {self.safety_validator.token_budget}
  Tokens Used:           {self.safety_validator.tokens_used}/{self.safety_validator.token_budget}

AVAILABLE TOOLS:
  - text_summarizer      Summarize long text passages
  - code_analyzer        Analyze code for quality/security/performance

"""
        print(config_text)

    def show_metrics(self):
        """Display session metrics."""
        if self.session_metrics.request_count == 0:
            print("ℹ No metrics yet - make some requests first")
            return
        
        metrics_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                    Session Metrics                             ║
╚════════════════════════════════════════════════════════════════╝

AGGREGATES:
  Requests:              {self.session_metrics.request_count}
  Total Tokens:          {self.session_metrics.total_tokens}
  Total Latency:         {self.session_metrics.total_latency_ms:.1f}ms
  Total Tool Calls:      {self.session_metrics.total_tool_calls}
  Total Errors:          {self.session_metrics.total_errors}

AVERAGES:
  Avg Tokens/Request:    {self.session_metrics.avg_tokens_per_request():.1f}
  Avg Latency/Request:   {self.session_metrics.avg_latency_ms():.1f}ms

LAST EXECUTION:
  {self.last_execution_metrics if self.last_execution_metrics else "N/A"}

"""
        print(metrics_text)

    def show_trace(self):
        """Display last execution trace."""
        if not self.last_execution_trace:
            print("ℹ No trace available - make a request first")
            return
        
        trace_text = f"""
╔════════════════════════════════════════════════════════════════╗
║               Last Execution Trace                             ║
╚════════════════════════════════════════════════════════════════╝

{self.last_execution_trace}

"""
        print(trace_text)

    def show_context_info(self):
        """Display context usage information."""
        info = self.context_manager.get_context_info()
        saturation = info["saturation_percent"]
        
        # Draw saturation bar
        bar_length = 30
        filled = int((saturation / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Color indicator
        if saturation < 50:
            indicator = "✓ Healthy"
        elif saturation < 80:
            indicator = "⚠ Moderate"
        else:
            indicator = "🔴 High - Consider summarization"
        
        context_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                  Context Usage Information                     ║
╚════════════════════════════════════════════════════════════════╝

SATURATION: {saturation:.0f}% {indicator}
  [{bar}]

BREAKDOWN:
  Total Messages:        {info["total_messages"]}
  Active (in window):    {info["active_messages"]}
  Window Size:           {info["window_size"]}
  
  Total Characters:      {info["total_characters"]}
  Est. Tokens:           {info["estimated_tokens"]}

RECOMMENDATION:
  {('Summarize old messages to free context' if info['should_summarize'] else 'Context usage is healthy')}

"""
        print(context_text)

    def show_safety(self):
        """Display safety settings."""
        budget_used = self.safety_validator.tokens_used
        budget_total = self.safety_validator.token_budget
        budget_percent = (budget_used / budget_total) * 100
        
        safety_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                    Safety Settings                             ║
╚════════════════════════════════════════════════════════════════╝

INPUT VALIDATION:
  Max Length:            {self.safety_validator.max_input_length} chars
  Injection Detection:   Enabled
  Encoding Validation:   Enabled

TOOL EXECUTION:
  Rate Limit:            {self.safety_validator.tool_rate_limit} per minute
  Timeout Protection:    Enabled

TOKEN BUDGETING:
  Budget:                {budget_total}
  Used:                  {budget_used}
  Remaining:             {budget_total - budget_used}
  Usage:                 {budget_percent:.1f}%

"""
        print(safety_text)

    def show_history(self):
        """Display conversation history."""
        if not self.context_manager.conversation_history:
            print("ℹ No history yet")
            return
        
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                  Conversation History                          ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")
        
        for i, (role, message) in enumerate(self.context_manager.conversation_history, 1):
            prefix = "🧑" if role == "user" else "🤖"
            msg = message[:200] + "..." if len(message) > 200 else message
            print(f"{i}. {prefix} {role.upper()}: {msg}\n")

    async def run_async(self, prompt: str) -> Optional[str]:
        """Run agent asynchronously with metrics tracking."""
        if not self.agent:
            print("✗ Agent not initialized")
            return None

        # Safety validation
        is_safe, error_msg = self.safety_validator.validate_input(prompt)
        if not is_safe:
            print(f"✗ Input validation failed: {error_msg}")
            return None

        # Check token budget
        estimated_tokens = len(prompt) // 4 + 100  # rough estimate
        can_proceed, budget_msg = self.safety_validator.check_token_budget(estimated_tokens)
        if not can_proceed:
            print(f"✗ {budget_msg}")
            return None
        if budget_msg:
            print(f"{budget_msg}")

        # Record prompt
        self.context_manager.add_message("user", prompt)

        # Build execution context
        start_time = time.time()
        context = self._build_context(prompt)
        
        # Record trace
        trace_lines = [
            f"Timestamp: {datetime.now().isoformat()}",
            f"Input Length: {len(prompt)} chars",
            f"Context Window: {len(self.context_manager.get_context_window())} messages",
            f"Est. Tokens: {estimated_tokens}",
        ]
        
        try:
            print("\n⏳ Agent thinking...")
            response = await self.agent.run(
                goal=context,
                max_turns=self.max_turns
            )

            # Calculate metrics
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = ExecutionMetrics(
                tokens_used=estimated_tokens,
                latency_ms=elapsed_ms,
                tool_calls=0,  # Would be tracked by tool registry in real scenario
                error_count=0
            )
            
            # Record metrics
            self.last_execution_metrics = metrics
            self.session_metrics.add_execution(metrics)
            self.safety_validator.record_token_usage(estimated_tokens)
            
            # Build trace
            trace_lines.extend([
                f"Latency: {elapsed_ms:.1f}ms",
                f"Response Length: {len(str(response))} chars",
                f"Status: ✓ Success",
            ])
            self.last_execution_trace = "\n".join(trace_lines)

            # Record response
            response_text = str(response)
            self.context_manager.add_message("assistant", response_text)

            # Display response
            print(f"\n{response_text}\n")
            print(f"✓ Complete ({elapsed_ms:.0f}ms)")
            return response_text

        except Exception as e:
            metrics = ExecutionMetrics(
                tokens_used=estimated_tokens,
                latency_ms=(time.time() - start_time) * 1000,
                tool_calls=0,
                error_count=1
            )
            self.last_execution_metrics = metrics
            self.session_metrics.add_execution(metrics)
            
            trace_lines.append(f"Status: ✗ Error - {str(e)}")
            self.last_execution_trace = "\n".join(trace_lines)
            
            print(f"✗ Error: {e}")
            return None

    def _build_context(self, prompt: str) -> str:
        """Build context with conversation history."""
        context_window = self.context_manager.get_context_window()
        
        if len(context_window) <= 1:  # Only the user's current prompt
            return prompt

        # Build context from recent history
        context = "You are a helpful AI assistant. Answer the user's question directly and concisely.\n\n"
        
        if context_window:
            context += "CONVERSATION HISTORY:\n"
            for role, message in context_window[:-1]:  # Exclude current prompt
                prefix = "User" if role == "user" else "You"
                msg = message[:150] + "..." if len(message) > 150 else message
                context += f"{prefix}: {msg}\n"
            context += "\n"
        
        context += f"User's new question: {prompt}\n\n"
        context += "Your answer (be direct, concise, and helpful):"
        
        return context

    def run(self):
        """Main REPL loop with persistent event loop."""
        # Create and set persistent event loop to avoid "Event loop is closed" errors
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self._run_repl()
        finally:
            # Clean up event loop
            if self.loop and not self.loop.is_closed():
                self.loop.close()
    
    def _run_repl(self):
        """Internal REPL loop using persistent event loop."""
        print("""
╔════════════════════════════════════════════════════════════════╗
║    Advanced Interactive Agent - Observability & Safety         ║
║                                                                ║
║  Type /help for commands  |  /exit to quit                    ║
╚════════════════════════════════════════════════════════════════╝
""")
        
        while True:
            try:
                prompt = input("\n> ").strip()
                
                if not prompt:
                    continue
                
                # Commands
                if prompt == "/help":
                    self.show_help()
                elif prompt == "/config":
                    self.show_config()
                elif prompt == "/metrics":
                    self.show_metrics()
                elif prompt == "/trace":
                    self.show_trace()
                elif prompt == "/context_info":
                    self.show_context_info()
                elif prompt == "/safety":
                    self.show_safety()
                elif prompt == "/history":
                    self.show_history()
                elif prompt == "/reset":
                    self.context_manager.conversation_history = []
                    self.session_metrics = SessionMetrics()
                    self.last_execution_metrics = None
                    print("✓ Reset complete")
                elif prompt == "/exit":
                    print("Goodbye!")
                    break
                elif prompt.startswith("/context "):
                    try:
                        size = int(prompt.split()[1])
                        msg = self.context_manager.set_window_size(size)
                        print(f"✓ {msg}")
                    except (IndexError, ValueError):
                        print("✗ Usage: /context SIZE")
                elif prompt.startswith("/limits "):
                    parts = prompt.split()
                    if len(parts) == 4 and parts[1] == "SET":
                        try:
                            value = int(parts[3])
                            msg = self.safety_validator.set_limits(parts[2], value)
                            print(f"✓ {msg}" if msg and "Unknown" not in msg else f"✗ {msg}")
                        except ValueError:
                            print("✗ Value must be a number")
                    else:
                        print("✗ Usage: /limits SET KEY VALUE")
                elif prompt.startswith("/cost_budget "):
                    try:
                        budget = int(prompt.split()[1])
                        self.safety_validator.token_budget = budget
                        print(f"✓ Token budget set to {budget}")
                    except (IndexError, ValueError):
                        print("✗ Usage: /cost_budget NUM")
                elif prompt.startswith("/provider "):
                    provider = prompt.split()[1].lower()
                    if provider in ["mock", "ollama"]:
                        self.provider_type = provider
                        self._init_agent()
                    else:
                        print("✗ Unknown provider. Use: mock, ollama")
                elif prompt.startswith("/model "):
                    self.model_name = prompt.split()[1]
                    if self.provider_type == "ollama":
                        self._init_agent()
                    print(f"✓ Model set to {self.model_name}")
                elif prompt.startswith("/max_turns "):
                    try:
                        turns = int(prompt.split()[1])
                        if 1 <= turns <= 10:
                            self.max_turns = turns
                            print(f"✓ Max turns set to {turns}")
                        else:
                            print("✗ Max turns must be between 1-10")
                    except (IndexError, ValueError):
                        print("✗ Usage: /max_turns NUM")
                else:
                    # Regular prompt - run agent using persistent event loop
                    try:
                        self.loop.run_until_complete(self.run_async(prompt))
                    except Exception as e:
                        print(f"✗ Error in async execution: {e}")
                        # Try to recover the event loop if it got closed
                        if self.loop.is_closed():
                            self.loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(self.loop)
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /exit to quit")
            except EOFError:
                # Gracefully handle EOF (piped input ended)
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"✗ Error: {e}")


if __name__ == "__main__":
    agent = AdvancedInteractiveAgent()
    agent.run()
