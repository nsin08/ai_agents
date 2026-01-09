"""
Hello World agent example.
"""

import asyncio
import os

from src.agent_labs.llm_providers import MockProvider, OllamaProvider
from src.agent_labs.orchestrator import Agent


async def main() -> None:
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    if use_ollama:
        provider = OllamaProvider(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama2"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "60")),
        )
    else:
        provider = MockProvider()
    agent = Agent(provider=provider)
    result = await agent.run("Say hello in one sentence.", max_turns=1)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
