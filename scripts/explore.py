#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exploration Notebook - Script-Based Agent Interaction

Perfect for learning and documentation. Loads agents and runs predefined scenarios
with real LLM providers (Ollama by default, cloud providers coming soon).

Usage:
    python scripts/explore.py              # Run default scenarios with Ollama
    python scripts/explore.py --custom      # Run custom scenario
    python scripts/explore.py --list        # List available scenarios
    
Prerequisites:
    - Ollama installed and running: ollama serve
    - Model downloaded: ollama pull llama2
"""

import sys
import io

# Fix Windows console encoding
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider, OllamaProvider, CloudProvider


@dataclass
class Scenario:
    """A scenario for agent exploration."""

    name: str
    description: str
    provider: str  # "ollama", "cloud", or "mock"
    model: str
    max_turns: int
    prompts: List[str]


class ExplorationNotebook:
    """Predefined agent exploration scenarios."""

    SCENARIOS = {
        "quickstart": Scenario(
            name="Quick Start",
            description="Simple introductory prompts with Ollama",
            provider="ollama",
            model="llama2",
            max_turns=3,
            prompts=[
                "What is artificial intelligence?",
                "How do agents work?",
                "What is machine learning?",
            ],
        ),
        "reasoning": Scenario(
            
            name="Reasoning & Logic",
            description="Test agent's reasoning capabilities",
            provider="ollama",
            model="llama2",
            max_turns=5,
            prompts=[
                "Solve this riddle: I have cities but no houses. What am I?",
                "Explain the concept of recursion",
                "What's the capital of France?",
            ],
        ),
        "storytelling": Scenario(
            name="Creative Storytelling",
            description="Agent creates stories and narratives",
            provider="ollama",
            model="llama2",
            max_turns=5,
            prompts=[
                "Tell me a short story about a robot learning to dance",
                "Write a haiku about artificial intelligence",
                "Describe an interesting utopia",
            ],
        ),
        "teaching": Scenario(
            name="Teaching & Explanation",
            description="Agent explains complex topics",
            provider="ollama",
            model="llama2",
            max_turns=5,
            prompts=[
                "Explain blockchain technology to a 5-year-old",
                "What are neural networks and how do they work?",
                "Describe quantum computing in simple terms",
            ],
        ),
    }

    ADVANCED_SCENARIOS = {
        "advanced": Scenario(
            name="Advanced Reasoning",
            description="Complex reasoning with real LLM",
            provider="ollama",
            model="llama2",
            max_turns=5,
            prompts=[
                "Design a simple machine learning pipeline for image classification",
                "What are the ethical implications of AI?",
                "How would you build a recommendation system?",
            ],
        ),
        "mock": Scenario(
            name="Mock Testing",
            description="Fast deterministic testing with MockProvider",
            provider="mock",
            model="mock",
            max_turns=3,
            prompts=[
                "Test prompt 1",
                "Test prompt 2",
                "Test prompt 3",
            ],
        ),
    }
    
    # Future cloud provider scenarios (requires implementation in cloud.py)
    CLOUD_SCENARIOS = {
        "cloud": Scenario(
            name="Cloud Provider",
            description="[Coming Soon] Use cloud LLM providers (OpenAI, Anthropic, etc.)",
            provider="cloud",
            model="gpt-4",
            max_turns=5,
            prompts=[
                "Explain quantum computing",
                "Write a poem about AI",
            ],
        ),
    }

    def __init__(self):
        self.all_scenarios = {**self.SCENARIOS, **self.ADVANCED_SCENARIOS, **self.CLOUD_SCENARIOS}

    def list_scenarios(self):
        """List all available scenarios."""
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║              Available Exploration Scenarios                  ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")

        for key, scenario in self.all_scenarios.items():
            print(f"📚 {key.upper()}")
            print(f"   Name: {scenario.name}")
            print(f"   Description: {scenario.description}")
            print(f"   Provider: {scenario.provider}")
            print(f"   Prompts: {len(scenario.prompts)}")
            print()

    async def run_scenario(self, scenario_key: str):
        """Run a scenario."""
        if scenario_key not in self.all_scenarios:
            print(f"✗ Unknown scenario: {scenario_key}")
            self.list_scenarios()
            return

        scenario = self.all_scenarios[scenario_key]

        print(f"\n╔════════════════════════════════════════════════════════════════╗")
        print(f"║  {scenario.name:<60}║")
        print(f"╚════════════════════════════════════════════════════════════════╝\n")
        print(f"Description: {scenario.description}\n")
        print(f"Configuration:")
        print(f"  Provider:  {scenario.provider}")
        print(f"  Model:     {scenario.model}")
        print(f"  Max Turns: {scenario.max_turns}\n")

        # Create provider
        if scenario.provider == "mock":
            provider = MockProvider()
        elif scenario.provider == "ollama":
            provider = OllamaProvider(
                model=scenario.model,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
        elif scenario.provider == "cloud":
            # Cloud provider requires implementation in cloud.py
            print("⚠️  CloudProvider is not yet implemented.")
            print("    To use cloud providers (OpenAI, Anthropic, etc.):")
            print("    1. Implement the CloudProvider class in src/agent_labs/llm_providers/cloud.py")
            print("    2. Add API key configuration")
            print("    3. Run this scenario again")
            print("\n    For now, use 'ollama' provider scenarios.\n")
            return
        else:
            print(f"✗ Unknown provider: {scenario.provider}")
            return

        agent = Agent(provider=provider)

        # Run each prompt
        for i, prompt in enumerate(scenario.prompts, 1):
            print(
                f"\n{'─' * 64}"
            )
            print(f"Prompt {i}/{len(scenario.prompts)}")
            print(f"{'─' * 64}")
            print(f"\n📝 {prompt}\n")
            print("⏳ Agent processing...\n")

            try:
                result = await agent.run(prompt, max_turns=scenario.max_turns)
                print(f"✓ Response:\n{result}\n")
            except Exception as e:
                print(f"✗ Error: {e}\n")
                import traceback

                traceback.print_exc()

        print(f"\n{'═' * 64}")
        print(f"✓ Scenario '{scenario_key}' completed successfully!")
        print(f"{'═' * 64}\n")

    def show_help(self):
        """Show help."""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║          Agent Exploration Notebook - Help                    ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  python scripts/explore.py              # Run default (quickstart with Ollama)
  python scripts/explore.py SCENARIO      # Run specific scenario
  python scripts/explore.py --list        # List all scenarios
  python scripts/explore.py --help        # Show this help

AVAILABLE SCENARIOS:
  quickstart   - Simple introductory prompts (Ollama)
  reasoning    - Test logical reasoning (Ollama)
  storytelling - Creative story generation (Ollama)
  teaching     - Complex topic explanations (Ollama)
  advanced     - Advanced reasoning tasks (Ollama)
  mock         - Fast testing with MockProvider
  cloud        - [Coming Soon] Cloud provider integration

PREREQUISITES:
  For Ollama scenarios (default):
    1. Install Ollama: https://ollama.ai/download
    2. Start server: ollama serve
    3. Pull model: ollama pull llama2
  
  For Cloud scenarios (future):
    Implementation required in cloud.py

EXAMPLES:
  python scripts/explore.py quickstart    # Default: uses Ollama + llama2
  python scripts/explore.py reasoning
  python scripts/explore.py teaching
  python scripts/explore.py mock          # Fast testing without LLM

WHAT TO EXPECT:
  Each scenario runs multiple prompts through the agent.
  The agent processes each prompt through its reasoning loop:
    1. OBSERVE the goal
    2. PLAN an approach
    3. ACT on the plan
    4. VERIFY the result
    5. REFINE if needed (up to max_turns)
  
OUTPUT:
  See agent responses showing its reasoning process and final answer.
        """
        print(help_text)


async def main():
    """Entry point."""
    notebook = ExplorationNotebook()

    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        notebook.show_help()
        return

    if sys.argv[1] == "--list":
        notebook.list_scenarios()
        return

    scenario_key = sys.argv[1].lower()
    await notebook.run_scenario(scenario_key)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
