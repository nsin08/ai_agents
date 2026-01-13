# Beginner Quick Reference Guide (1-Page Cheat Sheet)

**Level**: Beginner  
**Use**: Quick lookup while coding  
**Print**: Yes, fits on 1-2 pages

---

## Essential Commands

```bash
# Virtual Environment
uv venv                           # Create virtual environment
source .venv/bin/activate        # Activate (Linux/Mac)
.venv\Scripts\activate           # Activate (Windows)
pip install package-name         # Install packages

# Git
git clone <url>                  # Download repository
git status                       # See changes
git add file.py                  # Stage file
git commit -m "message"          # Commit changes
git push                         # Push to remote

# Testing
pytest tests/                    # Run all tests
pytest tests/test_file.py -v    # Run with output
pytest --cov=src                # Coverage report

# Run Code
python script.py                # Execute Python file
python -m pytest                # Run tests via module
python -i script.py             # Interactive mode
```

---

## Python Patterns

```python
# Creating an Agent
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider
from agent_labs.memory import ConversationMemory

provider = MockProvider()  # or OpenAIProvider, OllamaProvider
memory = ConversationMemory(max_turns=10)
agent = AgentOrchestrator(llm_provider=provider, memory=memory)

# Using an Agent
response = agent.run("Your question here")
print(response)

# Working with Memory
memory.add_turn("user", "message")
history = memory.get_history()
memory.clear()

# Building a Tool
class MyTool:
    name = "my_tool"
    description = "What it does"
    
    def execute(self, *args, **kwargs):
        # Implementation
        return result
```

---

## Common Patterns by Chapter

### Ch 1: Setup
```python
# Verify environment
python --version                # Should be 3.11+
uv --version
pytest --version
```

### Ch 2: Agent Loop
```python
# Interactive agent
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break
    response = agent.run(user_input)
    print(f"Agent: {response}")
```

### Ch 3: RAG
```python
from agent_labs.tools import VectorRetriever
from agent_labs.memory import DocumentStore

doc_store = DocumentStore()
retriever = VectorRetriever(doc_store, top_k=3)
agent.tools.append(retriever)
```

### Ch 4: Tools
```python
# Tool selection
if "calculate" in user_input.lower():
    result = calculator.execute(operation, a, b)
elif "weather" in user_input.lower():
    result = weather_tool.execute(city)
```

### Ch 5: Memory Persistence
```python
import json
from pathlib import Path

def save_preferences(data, file="prefs.json"):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def load_preferences(file="prefs.json"):
    return json.load(open(file)) if Path(file).exists() else {}
```

### Ch 6: Testing
```python
import pytest

def test_my_feature():
    """Test description"""
    result = function_to_test(input_value)
    assert result == expected_value
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'agent_labs'` | Install: `uv pip install -r requirements.txt` |
| `NameError: name 'XYZ' is not defined` | Add import: `from module import XYZ` |
| `pytest: command not found` | Install: `pip install pytest` |
| `virtual environment not activated` | Run: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows) |
| `git: command not found` | Install Git from https://git-scm.com/downloads |
| `Python version too old` | Download 3.11+ from https://python.org |
| Agent doesn't remember (no memory) | Add: `memory = ConversationMemory(max_turns=10)` and pass to agent |
| Test fails randomly | Switch to MockProvider instead of real LLM |

---

## File Locations

```
ai_agents/
├── labs/
│   ├── 00/                    # Environment (Chapter 1)
│   ├── 01/                    # RAG (Chapter 3)
│   ├── 02/                    # Tools (Chapter 4)
│   └── 04/                    # Memory (Chapter 5)
├── curriculum/presentable/01_beginner/
│   ├── chapter_01_*.md        # Chapters
│   └── ...
├── src/agent_labs/
│   ├── orchestrator/          # Agent core
│   ├── llm_providers/         # Providers (OpenAI, Mock, Ollama)
│   ├── memory/                # Memory systems
│   ├── tools/                 # Tool implementations
│   └── ...
└── tests/                     # Test files
```

---

## Key Classes & Methods

| Class | Method | Purpose |
|-------|--------|---------|
| `AgentOrchestrator` | `run(text)` | Send message, get response |
| `MockProvider` | `generate(prompt)` | Returns mock response (echoes) |
| `OpenAIProvider` | `generate(prompt)` | Calls GPT-4/GPT-3.5 |
| `OllamaProvider` | `generate(prompt)` | Calls local LLM |
| `ConversationMemory` | `add_turn(role, text)` | Add message to memory |
| `ConversationMemory` | `get_history()` | Retrieve all messages |
| `DocumentStore` | `search(query)` | Find documents |
| `VectorRetriever` | `execute(query)` | RAG retrieval |

---

## Decision Trees

### Which Provider to Use?
```
Do you want to test locally?
├─ YES → Use MockProvider (instant, free)
└─ NO → Do you have an API key?
    ├─ YES (OpenAI) → Use OpenAIProvider
    └─ YES (Local) → Use OllamaProvider
```

### How to Store Data?
```
Does data need to survive restart?
├─ NO → Use ConversationMemory (RAM-based)
└─ YES → Use JSON file or LongTermMemory
    ├─ Simple → JSON with open()/json.dump()
    └─ Complex → Database (later curriculum)
```

### Should I Test It?
```
Is it part of core functionality?
├─ YES → Write unit test
├─ Tools? → Test tool behavior
├─ Memory? → Test persistence
└─ User-facing? → Write integration test
```

---

## Common Mistakes & Fixes

| ❌ Wrong | ✅ Right |
|---------|----------|
| No imports | Add `from module import Class` |
| Unactivated venv | Always activate before running |
| No memory in agent | Pass `memory=ConversationMemory()` |
| Tool execution fails silently | Always wrap in try/except |
| Memory grows forever | Set `max_turns` limit |
| Test uses real LLM | Switch to MockProvider |
| No error handling | Add `assert` statements in tests |
| Ignoring error messages | READ the error—it tells you what's wrong |

---

## Learning Resources

| Topic | Resource |
|-------|----------|
| Python Basics | https://python.org/doc |
| pytest | https://pytest.org/doc |
| Git | https://git-scm.com/doc |
| LangChain | https://langchain.readthedocs.io |
| OpenAI API | https://platform.openai.com/docs |
| Ollama | https://ollama.ai |

---

## Quick Checklist Before Moving to Intermediate

- [ ] Completed all 7 chapters
- [ ] Solved all 21 exercises
- [ ] Wrote and ran tests
- [ ] Built a small project
- [ ] Understand agent loop (observe → plan → act)
- [ ] Know the difference: tools vs memory vs RAG
- [ ] Can explain: embeddings, tokens, hallucination
- [ ] Feel confident running Python + pytest + git

**Ready?** → Move to Intermediate curriculum!

---

## Emergency Debugging Script

```python
# Copy this when stuck (debug_helper.py)
import sys
from pathlib import Path

print(f"Python: {sys.version}")
print(f"Working Dir: {Path.cwd()}")
print(f"Virtual Env: {sys.prefix}")

# Check imports
try:
    from agent_labs.orchestrator import AgentOrchestrator
    print("✓ agent_labs installed")
except ImportError:
    print("✗ agent_labs NOT installed")

try:
    import pytest
    print("✓ pytest installed")
except ImportError:
    print("✗ pytest NOT installed")

# List installed packages
import subprocess
print("\nInstalled packages:")
subprocess.run(["pip", "list"])
```

Run with: `python debug_helper.py`

---

## Final Tips

1. **Read error messages** - They're your friend
2. **Google the error** - Odds are someone had it before
3. **Print debugging** - `print(variable)` to see what's happening
4. **Test incrementally** - Change one thing at a time
5. **Ask for help** - Show your error message + code
6. **Break problems down** - Don't build everything at once
7. **Read the docs** - Library docs have examples
8. **Version control always** - Use git from day 1
9. **Test early** - Write tests while coding, not after
10. **Have fun** - You're building AI agents! 🚀

---

**Bookmark this page!** Return here whenever you need a quick lookup.

Last Updated: January 2026 | For Beginner Curriculum

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Scannable sections with short bullets
- [ ] Commands and tips included
- [ ] ASCII only
