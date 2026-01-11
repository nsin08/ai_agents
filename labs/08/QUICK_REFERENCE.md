# Lab 8: Quick Reference

## Quick Start
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

result = system.run("Research Python and write tutorial and implement code")
print(result)
```

## Core Methods
```python
system.register_agent("research", ResearchAgent())
agent_name = system.route_task("research Python")
subtasks = system.decompose("research X and write Y")
result = system.delegate("research X", "research")
final = system.combine([result])
messages = system.get_communication_flow()
stats = system.get_statistics()
```

## Statistics (actual keys)
```python
# Example output
{
  "registered_agents": 3,
  "total_messages": 12,
  "agent_list": ["research", "writing", "coding"]
}
```

## Communication Flow (actual keys)
```python
for msg in system.get_communication_flow():
    print(f"{msg['from']} -> {msg['to']}: {msg['content']}")
```

## Common Issues
- No agent selected: ensure `get_capabilities()` matches task keywords.
- Empty system: register at least one agent before routing.
- Poor output merge: customize `combine()`.
