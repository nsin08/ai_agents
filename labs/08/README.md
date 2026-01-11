# Lab 8: Multi-Agent Systems

## Overview
Multi-agent systems use multiple specialized agents to solve complex tasks through coordination and routing.
This lab focuses on router and decomposition patterns with optional extensions to hierarchical and swarm designs.

## Key Concepts
- Agent coordination and communication
- Task routing based on capabilities
- Task decomposition into subtasks
- Result combination and traceability
- Scaling by adding new specialists

## Architecture Overview
```
User Task
  -> MultiAgentSystem
     -> decompose(task)
     -> route_task(subtask)
     -> delegate(subtask, agent)
     -> combine(results)
```

## Core Interfaces (reference)
```python
from typing import List, Protocol

class Agent(Protocol):
    def run(self, task: str) -> str:
        ...
    def get_capabilities(self) -> List[str]:
        ...
```

## Patterns
1) Router Pattern: route each subtask to the best specialist by capability keywords.
2) Decomposition Pattern: split tasks using "and" and route each part.
3) Intelligent Routing: capability score + load balancing (exercise 3).
4) Hierarchical Pattern: manager + team leads + specialists.
5) Swarm Pattern: peer agents collaborate via shared memory.

## Quick Start
```bash
# From repo root
$env:PYTHONPATH='.'; python labs/08/src/multi_agent_system.py
$env:PYTHONPATH='.'; pytest labs/08/tests/test_multi_agent_system.py -v --capture=tee-sys
```

## Example Usage
```python
import sys
from pathlib import Path

# Add labs/08/src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "labs" / "08" / "src"))

from multi_agent_system import MultiAgentSystem
from specialist_agents import ResearchAgent, WritingAgent, CodingAgent

system = MultiAgentSystem(verbose=True)
system.register_agent("research", ResearchAgent())
system.register_agent("writing", WritingAgent())
system.register_agent("coding", CodingAgent())

result = system.run("Research async and write tutorial and implement code")
print(result)
```

## Exercises
- Exercise 1: Basic coordination with router + decomposition.
- Exercise 2: Add a third specialist and validate 3-agent flow.
- Exercise 3: Implement intelligent routing with load balancing.

## Files
- `START_HERE.md` - Guided start and learning path
- `QUICK_REFERENCE.md` - Method and pattern cheat sheet
- `STRUCTURE.md` - Directory map
- `COMPLETION_CHECKLIST.md` - Requirements checklist
- `DELIVERY_REPORT.md` - Summary and validation
- `src/multi_agent_system.py` - Core router/orchestrator
- `src/specialist_agents.py` - Specialist agents
- `tests/test_multi_agent_system.py` - Test suite
- `exercises/` - Progressive exercises

## Troubleshooting
- No agent selected: verify `get_capabilities()` matches task keywords.
- Poor combination: adjust `combine()` format.
- Empty system: register at least one agent before routing.

## References
- Related labs: Orchestrator, Memory, Observability
- Framework: https://github.com/nsin08/space_framework

Last updated: 2026-01-10
