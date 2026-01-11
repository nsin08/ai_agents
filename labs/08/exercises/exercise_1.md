# Exercise 1: Run System with 2 Agents

## Objective
Run a basic multi-agent system (Research + Writing) and observe routing and results.

## Steps
1. Create a script `exercise_1_run_system.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "labs" / "08" / "src"))

from multi_agent_system import MultiAgentSystem
from specialist_agents import ResearchAgent, WritingAgent

system = MultiAgentSystem(verbose=True)
system.register_agent("research", ResearchAgent())
system.register_agent("writing", WritingAgent())

task = "Research machine learning and write a summary"
print(f"
Task: {task}
")
result = system.run(task)
print(result)
```
2. Run it:
```bash
$env:PYTHONPATH='.'; python labs/08/exercises/exercise_1_run_system.py
```
3. Capture:
- Subtasks identified
- Which agent handled each subtask
- Combined result format

## Deliverable
Create `EXERCISE_1_RESULTS.md` with:
- Subtask list
- Agent routing decisions
- Combined output notes
