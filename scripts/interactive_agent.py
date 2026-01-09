#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Agent Playground

A REPL-style interface to interact with AI agents for experimentation and learning.
Supports both MockProvider (fast, deterministic) and OllamaProvider (local LLM).

Usage:
    python scripts/interactive_agent.py

Commands:
    /help           - Show available commands
    /config         - Show current agent configuration
    /reset          - Reset agent memory and state
    /provider TYPE  - Switch provider (mock, ollama)
    /model NAME     - Set model name (for ollama)
    /max_turns N    - Set max turns for agent
    /history        - Show conversation history
    /exit           - Exit the playground

Examples:
    > /config
    > What is the capital of France?
    > /reset
    > /provider ollama
    > Tell me about machine learning
"""

import sys
import io

# Fix Windows console encoding
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import os
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent, AgentState
from agent_labs.llm_providers import MockProvider, OllamaProvider
from agent_labs.memory import MemoryManager, ShortTermMemory, LongTermMemory


class InteractiveAgent:
    """Interactive agent playground with command support."""

    def __init__(self):
        self.agent: Optional[Agent] = None
        self.provider_type = "mock"
        self.model_name = "llama2"
        self.max_turns = 3
        self.conversation_history = []
        self._init_agent()

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
            self.conversation_history = []
        except Exception as e:
            print(f"✗ Error initializing agent: {e}")
            self.agent = None

    def show_help(self):
        """Display help information."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║            Interactive Agent Playground - Help Menu            ║
╚════════════════════════════════════════════════════════════════╝

COMMANDS:
  /help              Show this help message
  /config            Display current agent configuration
  /reset             Clear conversation history and agent state
  /provider TYPE     Switch provider: 'mock' or 'ollama'
  //model NAME        Set model name (e.g., 'llama2', 'mistral')
  /max_turns N       Set maximum turns for agent response (1-10)
  /history           Show full conversation history
  /exit              Exit the playground

USAGE:
  Simply type your prompt and press Enter to interact with the agent.
  The agent will reason through your request in up to max_turns iterations.

EXAMPLES:
  > /config
  > What is machine learning?
  > /provider ollama
  > /model mistral
  > /max_turns 5
  > Explain the capital of France
  > /history
  > /reset

NOTES:
  - MockProvider gives instant, deterministic responses
  - OllamaProvider requires Ollama running locally (ollama serve)
  - Pull models first: ollama pull llama2
  - Agent uses memory to track conversation context
        """
        print(help_text)

    def show_config(self):
        """Display current configuration."""
        config_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                  Agent Configuration                           ║
╚════════════════════════════════════════════════════════════════╝

Provider:           {self.provider_type.upper()}
Model:              {self.model_name}
Max Turns:          {self.max_turns}
Agent Status:       {'✓ Ready' if self.agent else '✗ Not initialized'}
History Size:       {len(self.conversation_history)} messages
        """
        print(config_text)

    def show_history(self):
        """Display conversation history."""
        if not self.conversation_history:
            print("\n[No conversation history yet]")
            return

        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                    Conversation History                        ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")

        for i, (role, message) in enumerate(self.conversation_history, 1):
            prefix = "YOU" if role == "user" else "AGENT"
            print(f"[{i}] {prefix}:")
            print(f"    {message}\n")

    def reset(self):
        """Reset agent state and history."""
        self.conversation_history = []
        self._init_agent()
        print("✓ Agent reset successfully")

    def _build_context_prompt(self, prompt: str) -> str:
        """Build a prompt that includes conversation context."""
        if not self.conversation_history:
            return prompt
        
        # Build context from recent history (last 10 messages to keep context manageable)
        recent_history = self.conversation_history[-10:]
        
        context = "You are a helpful AI assistant. Answer the user's question directly and concisely.\n\n"
        
        if recent_history:
            context += "CONVERSATION HISTORY:\n"
            for role, message in recent_history:
                prefix = "User" if role == "user" else "You"
                # Truncate very long messages
                msg = message[:150] + "..." if len(message) > 150 else message
                # Clean up "Executed:" prefix if present
                if msg.startswith("Executed:"):
                    msg = msg[9:].strip()
                context += f"{prefix}: {msg}\n"
            context += "\n"
        
        context += f"User's new question: {prompt}\n\n"
        context += "Your answer (be direct, concise, and helpful):"
        
        return context

    async def run_agent(self, prompt: str):
        """Run agent with given prompt."""
        if not self.agent or not self.agent.provider:
            print("✗ Provider not initialized. Try /reset")
            return

        try:
            print("\n⏳ Agent thinking...\n")
            
            # Inject conversation context into the prompt
            context_prompt = self._build_context_prompt(prompt)
            
            # Call LLM directly for conversational Q&A (bypass agent's goal-achievement loop)
            # The agent orchestrator is only needed for complex multi-step tasks
            response = await self.agent.provider.generate(context_prompt)
            result = response.text

            print("╔════════════════════════════════════════════════════════════════╗")
            print("║                      Agent Response                            ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            print(result)
            print()

            # Add to history (store original prompt, not context-injected version)
            self.conversation_history.append(("user", prompt))
            self.conversation_history.append(("agent", result))

        except Exception as e:
            print(f"✗ Error running agent: {e}")
            import traceback

            traceback.print_exc()

    def handle_command(self, command: str) -> bool:
        """
        Handle special commands.
        Returns True if command was handled, False otherwise.
        """
        cmd = command.strip().lower()

        if cmd == "/help":
            self.show_help()
            return True

        elif cmd == "/config":
            self.show_config()
            return True

        elif cmd == "/reset":
            self.reset()
            return True

        elif cmd == "/history":
            self.show_history()
            return True

        elif cmd == "/exit":
            print("\n👋 Goodbye!")
            sys.exit(0)

        elif cmd.startswith("/provider "):
            provider_type = cmd.split(" ", 1)[1].strip().lower()
            if provider_type in ["mock", "ollama"]:
                self.provider_type = provider_type
                self._init_agent()
                print(f"✓ Switched to {provider_type} provider")
            else:
                print(f"✗ Unknown provider: {provider_type}. Use 'mock' or 'ollama'")
            return True

        elif cmd.startswith("/model "):
            model_name = cmd.split(" ", 1)[1].strip()
            self.model_name = model_name
            self._init_agent()
            print(f"✓ Model set to {model_name}")
            return True

        elif cmd.startswith("/max_turns "):
            try:
                turns = int(cmd.split(" ", 1)[1].strip())
                if 1 <= turns <= 10:
                    self.max_turns = turns
                    print(f"✓ Max turns set to {turns}")
                else:
                    print("✗ Max turns must be between 1 and 10")
            except ValueError:
                print("✗ Invalid number for max_turns")
            return True

        return False

    async def main_loop(self):
        """Main interactive loop."""
        print("\n")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║         🤖 Interactive Agent Playground                       ║")
        print("║                                                                ║")
        print("║  Type /help for commands or ask me anything!                  ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
        self.show_config()

        while True:
            try:
                prompt = input("\n> ").strip()

                if not prompt:
                    continue

                if self.handle_command(prompt):
                    continue

                # Run agent with the prompt
                await self.run_agent(prompt)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"✗ Error: {e}")
                import traceback

                traceback.print_exc()


async def main():
    """Entry point."""
    playground = InteractiveAgent()
    await playground.main_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
