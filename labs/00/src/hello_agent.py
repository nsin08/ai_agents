"""
Hello World agent example.
"""

import asyncio
import os

from src.agent_labs.llm_providers import MockProvider, OllamaProvider
from src.agent_labs.orchestrator import Agent
from src.agent_labs.config import get_config, LLMProvider


async def main() -> None:
    # Load configuration from environment
    config = get_config()
    
    # Create provider based on configuration
    if config.provider == LLMProvider.MOCK:
        provider = MockProvider()
    elif config.provider == LLMProvider.OLLAMA:
        provider = OllamaProvider(
            base_url=config.provider_config.base_url,
            model=config.provider_config.model,
            timeout=config.provider_config.timeout,
        )
    else:
        raise ValueError(f"Unsupported provider: {config.provider.value}")
    
    agent = Agent(provider=provider)
    result = await agent.run("Say hello in one sentence.", max_turns=1)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
