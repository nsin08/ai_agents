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
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider, OllamaProvider, OpenAIProvider
from agent_labs.config import get_config, reload_config, ProviderConfig


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
        "openai": Scenario(
            name="OpenAI GPT-4",
            description="Use OpenAI GPT-4 for high-quality responses",
            provider="openai",
            model="gpt-4",
            max_turns=5,
            prompts=[
                "What is artificial intelligence?",
                "Explain quantum computing in simple terms",
                "What are the ethical implications of AI?",
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
        "anthropic": Scenario(
            name="Anthropic Claude",
            description="[Coming Soon] Use Anthropic Claude",
            provider="anthropic",
            model="claude-3-opus",
            max_turns=5,
            prompts=[
                "Explain quantum computing",
                "Write a poem about AI",
            ],
        ),
        "google": Scenario(
            name="Google Gemini",
            description="[Coming Soon] Use Google Gemini",
            provider="google",
            model="gemini-pro",
            max_turns=5,
            prompts=[
                "What is machine learning?",
                "Explain neural networks",
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

    async def run_scenario(self, scenario_key: str, override_provider: Optional[str] = None, override_model: Optional[str] = None):
        """Run a scenario with optional provider/model override."""
        if scenario_key not in self.all_scenarios:
            print(f"✗ Unknown scenario: {scenario_key}")
            self.list_scenarios()
            return

        scenario = self.all_scenarios[scenario_key]
        
        # Override provider and model if specified
        if override_provider:
            scenario.provider = override_provider
        if override_model:
            scenario.model = override_model

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
        elif scenario.provider == "openai":
            # OpenAI provider
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️  OpenAI API key not found.")
                print("    Set OPENAI_API_KEY environment variable in .env file")
                print("    Example: OPENAI_API_KEY=sk-...")
                return
            
            provider = OpenAIProvider(
                api_key=api_key,
                model=scenario.model,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                timeout=int(os.getenv("OPENAI_TIMEOUT", "30")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            )
        elif scenario.provider in ["anthropic", "google", "azure-openai"]:
            # Cloud providers not yet fully implemented
            print(f"⚠️  {scenario.provider.title()} provider is not yet fully implemented.")
            print(f"    To use {scenario.provider}:")
            print(f"    1. Implement the {scenario.provider.title()}Provider class")
            print(f"    2. Add API key configuration")
            print(f"    3. Run this scenario again")
            print(f"\n    For now, use 'ollama' or 'openai' provider scenarios.\n")
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
  openai       - Use OpenAI GPT-4 (requires OPENAI_API_KEY)
  storytelling - Creative story generation (Ollama)
  teaching     - Complex topic explanations (Ollama)
  advanced     - Advanced reasoning tasks (Ollama)
  mock         - Fast testing with MockProvider
  anthropic    - [Coming Soon] Anthropic Claude
  google       - [Coming Soon] Google Gemini

PREREQUISITES:
  For Ollama scenarios (default):
    1. Install Ollama: https://ollama.ai/download
    2. Start server: ollama serve
    3. Pull model: ollama pull llama2
  
  For OpenAI scenarios:
    1. Set OPENAI_API_KEY in .env file
    2. Example: OPENAI_API_KEY=sk-...
  
  For other cloud providers (Anthropic, Google):
    Implementation required in respective provider files

EXAMPLES:
  python scripts/explore.py quickstart    # Default: uses Ollama + llama2
  python scripts/explore.py reasoning
  python scripts/explore.py openai        # Uses OpenAI GPT-4 (requires API key)
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
    from dotenv import load_dotenv
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Agent Exploration Notebook - Run interactive agent scenarios',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available scenarios
  python scripts/explore.py --list
  
  # Run a scenario with defaults
  python scripts/explore.py reasoning
  
  # Override provider and model
  python scripts/explore.py reasoning --openai --model gpt-4
  python scripts/explore.py teaching --ollama --model llama3.2:3b
  python scripts/explore.py quickstart --mock
  
  # Override with specific model only
  python scripts/explore.py openai --model gpt-3.5-turbo
        """
    )
    parser.add_argument('scenario', nargs='?', default='quickstart',
                       help='Scenario to run (quickstart, reasoning, openai, teaching, etc.)')
    parser.add_argument('--list', action='store_true',
                       help='List all available scenarios and exit')
    parser.add_argument('--help-full', action='store_true',
                       help='Show full help with scenario descriptions')
    parser.add_argument('--ollama', action='store_true',
                       help='Override scenario provider to use Ollama')
    parser.add_argument('--openai', action='store_true',
                       help='Override scenario provider to use OpenAI (requires OPENAI_API_KEY)')
    parser.add_argument('--mock', action='store_true',
                       help='Override scenario provider to use Mock (deterministic responses)')
    parser.add_argument('--model', type=str,
                       help='Override model name (e.g., gpt-4, llama3.2:3b, etc.)')

    args = parser.parse_args()

    notebook = ExplorationNotebook()

    if args.list:
        notebook.list_scenarios()
        return

    if args.help_full:
        notebook.show_help()
        return

    # Determine provider override
    override_provider = None
    if args.openai:
        override_provider = "openai"
    elif args.ollama:
        override_provider = "ollama"
    elif args.mock:
        override_provider = "mock"

    # Validate OpenAI API key if openai provider is requested
    if override_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.strip() == "":
            print("✗ Error: OPENAI_API_KEY not set in environment")
            print("  Please set your OpenAI API key in .env file or environment")
            return

    # Run the scenario with overrides
    scenario_key = args.scenario.lower() if args.scenario else "quickstart"
    await notebook.run_scenario(scenario_key, override_provider, args.model)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
