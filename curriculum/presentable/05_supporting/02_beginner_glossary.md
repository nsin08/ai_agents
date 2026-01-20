# Beginner Glossary: AI Agents Terminology

**Level**: Beginner  
**Total Terms**: 40+  
**How to Use**: Reference while reading chapters, bookmark key terms

---

## A

### Agent
**Definition**: An autonomous AI system that observes, reasons, and acts to achieve goals.

**Example**: A customer support agent that reads support tickets, decides which team should handle them, and assigns them automatically.

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md): Your First Agent

---

### Activation (of virtual environment)
**Definition**: The process of "entering" a Python virtual environment so packages are isolated.

**Example**: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md): Environment Setup

**See Also**: Virtual Environment, venv

---

### Async / Asynchronous
**Definition**: Code that doesn't wait for operations to complete; multiple things happen simultaneously.

**Example**: Agent making 3 API calls at once instead of waiting for each one.

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md) (Python 3.11+ supports async)

---

## C

### Short-Term Memory (Conversation Memory)
**Definition**: Bounded memory that stores recent conversation turns (messages). In code, use `ShortTermMemory`.

**Example**:
```python
from agent_labs.memory import ShortTermMemory, MemoryItem

memory = ShortTermMemory(max_items=10)
memory.store(MemoryItem(role="user", content="Hello"))
```

**Related Chapter**: [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md): Memory and Context

**See Also**: Long-Term Memory, Memory Expiration

---

### Context Window
**Definition**: Maximum amount of text an LLM can process at once.

**Example**: GPT-4 has 8K token context (roughly 6,000 words). Longer conversations don't fit.

**Related Chapter**: [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md) (Token Management)

---

### Code Example / Runnable Code
**Definition**: Working Python code you can copy and run immediately.

**Where Found**: Every chapter includes 2-3 code examples.

---

## D

### Definition of Done (DoD)
**Definition**: Checklist of what must be complete before a story is considered finished.

**Example**: For [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md), all tests must pass, all exercises completed.

**Related Chapter**: Mentioned in acceptance criteria

---

### Definition of Ready (DoR)
**Definition**: Checklist of what must be true before starting work on something.

**Example**: Requirements are clear, dependencies are available.

---

### Dependencies
**Definition**: Other code libraries your project needs to function.

**Example**: pytest, agent_labs, pydantic are dependencies of this project.

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md) (uv installs dependencies)

**See Also**: Package Manager

---

### Document Store
**Definition**: Database of documents that agents can search and retrieve from.

**Example**: FAQ database, company handbook, knowledge base.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md): RAG Fundamentals

---

## E

### Embedding (Vector Embedding)
**Definition**: Conversion of text into a list of numbers (vector) that captures meaning.

**Example**: "dog" -> [0.8, 0.2, 0.1, ...]; "cat" -> [0.7, 0.3, 0.1, ...] (similar vectors = similar meaning)

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md): RAG Fundamentals

**Key Insight**: Similar meanings have similar vectors; enables semantic search.

---

### Environment (Python Environment)
**Definition**: Isolated Python installation specific to one project.

**Why**: Prevents package conflicts between projects.

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md): Environment Setup

**See Also**: Virtual Environment, venv

---

### Error Message
**Definition**: Text that explains what went wrong when code fails.

**Example**: `NameError: name 'Agent' is not defined`

**Pro Tip**: Read error messages carefully - they tell you exactly how to fix the problem.

---

## F

### Flow / Workflow
**Definition**: Step-by-step sequence of actions to accomplish a goal.

**Example**: Search documents -> Filter results -> Generate answer -> Send response.

**Related Chapter**: [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md) (Multi-Step Workflows)

---

## G

### Glossary
**Definition**: Alphabetical list of terms and definitions (you're reading this now!).

---

## H

### Hallucination
**Definition**: When an agent makes up false information not grounded in retrieved documents.

**Example**: Agent claims a policy says "30 days vacation" when documents say "15 days."

**Solution**: Use RAG, validate outputs, constrain with prompts.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md) (RAG prevents hallucination)

---

### Hello World / Hello Agent
**Definition**: Simple test program proving your environment works.

**Example**: `python labs/00/src/hello_agent.py`

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md): Environment Setup

---

## I

### Import (Python Import)
**Definition**: Loading code from another file or library into your script.

**Example**: `from agent_labs.orchestrator import Agent`

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md) (missing imports cause errors)

---

### Integration Test
**Definition**: Test that verifies components work together correctly.

**Example**: Test that Agent + Memory + Tools work as a system.

**Difference from Unit Test**: Unit tests one component; integration tests multiple.

**Related Chapter**: [Chapter 6: Testing Your Agent](../01_beginner/chapter_06_testing_your_agent.md): Testing Your Agent

---

## J

### JSON
**Definition**: Format for storing and transferring data (human-readable text).

**Example**: `{"name": "Sarah", "age": 30, "city": "Boston"}`

**Related Chapter**: Used for storing preferences ([Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md))

---

## K

### Knowledge Base
**Definition**: Collection of documents/facts an agent can search and reference.

**Example**: Company policies, product documentation, FAQs.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md): RAG Fundamentals

---

## L

### Lab / Laboratory
**Definition**: Hands-on coding exercise connected to each chapter.

**Structure**: 
- Lab 0: Environment Setup
- Lab 1: RAG
- Lab 2: Tools
- Lab 4: Memory

**Location**: `labs/` directory

---

### LLM (Large Language Model)
**Definition**: AI model trained on massive text data; can understand and generate language.

**Examples**: GPT-4, GPT-3.5, Claude, Llama 2

**Related Chapter**: Discussed in [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (Providers)

**See Also**: Provider

---

### Long-Term Memory
**Definition**: Persistent memory that survives across sessions (saved to disk).

**Example**: User preferences saved to JSON file; agent remembers them after restart.

**Related Chapter**: [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md): Memory and Context

**Contrast**: Short-Term Memory (session-only)

---

## M

### Memory
**Definition**: Agent's ability to remember past information.

**Types**:
- Short-Term Memory: Recent exchanges
- Long-Term Memory: Persistent facts
- Episodic Memory: Searchable past events

**Related Chapter**: [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md): Memory and Context

---

### MockProvider
**Definition**: Fake LLM that echoes input for testing (doesn't use real AI).

**Why Use**: Fast, cheap, predictable (no actual LLM calls).

**Limitation**: Not actually intelligent - just repeats.

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (Providers)

---

### Multi-Agent
**Definition**: System with multiple agents working together, each with different roles.

**Example**: One agent handles support, another handles billing, they collaborate.

**Related Chapter**: [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md) (multi-step workflows hint at this)

---

## O

### Ollama
**Definition**: Open-source tool for running local LLMs (no API key needed).

**Example**: Run Llama 2 locally on your computer.

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (Provider options)

---

### Observe-Plan-Act Loop
**Definition**: Core agent reasoning cycle: perceive situation -> decide action -> execute.

**Example**:
1. Observe: User asks "What's 5+3?"
2. Plan: "Need calculator tool"
3. Act: Call calculator

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (The Five-Step Loop)

---

### OpenAI Provider
**Definition**: Integration that calls OpenAI's API (GPT-4, GPT-3.5, etc.).

**Cost**: Charged per token used.

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (Provider options)

---

### Orchestrator
**Definition**: Component that coordinates all agent operations (memory, tools, reasoning).

**Analogy**: Orchestra conductor - manages all instruments working together.

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (Agent)

---

## P

### Package
**Definition**: Reusable code library installed via package manager.

**Examples**: pytest, agent_labs, numpy

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md) (uv installs packages)

**See Also**: Package Manager, Dependencies

---

### Package Manager
**Definition**: Tool that installs and manages Python packages.

**Examples**: uv (modern), pip (traditional)

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md): Environment Setup

---

### Parameter
**Definition**: Input variable a function/tool requires.

**Example**: Calculator's divide() needs parameters: a (dividend) and b (divisor).

**Related Chapter**: [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md) (Tool Parameters)

---

### Personality (System Prompt)
**Definition**: Instructions that customize an agent's behavior and tone.

**Example**: "You are a friendly pirate assistant" -> agent responds like a pirate.

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (system_prompt parameter)

---

### Provider
**Definition**: Source of LLM responses (OpenAI, Ollama, Mock, etc.).

**Analogy**: "Where the agent gets its intelligence from."

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md), Section 5 (LLM Providers)

---

### Python
**Definition**: Programming language used throughout this curriculum.

**Why Python**: Popular for AI, readable syntax, great libraries.

**Required Version**: 3.11+ (for async support and improvements)

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md)

---

## Q

### Quiz / Self-Assessment
**Definition**: Questions at end of each chapter to test understanding.

**Format**: Multiple choice, 10 questions per chapter.

**Answers**: Provided in chapter glossary sections.

---

## R

### RAG (Retrieval-Augmented Generation)
**Definition**: Technique where agent retrieves relevant documents then generates answers from them.

**Formula**: RAG = Retrieve + Generate

**Benefit**: Agent can answer from your documents, not just training data.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md): RAG Fundamentals

**See Also**: Embedding, Vector Search

---

### Repository
**Definition**: Folder containing all project code, usually on GitHub.

**Example**: https://github.com/nsin08/ai_agents

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md) (`git clone`)

---

### Retriever
**Definition**: Tool that searches documents and returns relevant ones.

**Example**: A vector retriever uses embeddings to find similar documents.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md) (RAG retrieval)

---

## S

### Semantic Search
**Definition**: Search by meaning (understanding concepts) rather than keywords.

**Example**: Query "How do I reset my password?" finds results for "password recovery" (same meaning, different words).

**Contrast**: Keyword search only matches exact words.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md) (Embeddings enable semantic search)

---

### State Machine
**Definition**: System with defined states and transitions between them.

**Example**: Agent states: Waiting -> Processing -> Responding -> Done

**Related Chapter**: Mentioned in orchestrator flow

---

### Storage / Persistent Storage
**Definition**: Saving data to disk (files, databases) so it survives program restart.

**Example**: `preferences.json` stores user preferences permanently.

**Related Chapter**: [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md) (Long-Term Memory)

---

### System Prompt
**Definition**: Instructions given to LLM that define behavior and personality.

**Example**: "You are a helpful assistant focused on customer support."

**Related Chapter**: [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md) (Personality Agent)

---

## T

### Test / Unit Test
**Definition**: Automated code that verifies other code works correctly.

**Example**: `assert calculator.add(2, 3) == 5`

**Why**: Catch bugs early, ensure changes don't break things.

**Related Chapter**: [Chapter 6: Testing Your Agent](../01_beginner/chapter_06_testing_your_agent.md): Testing Your Agent

---

### Tool (Agent Tool)
**Definition**: Function an agent can call to perform actions (not just generate text).

**Examples**: Calculator, weather API, database query, email sender.

**Related Chapter**: [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md): Tool Integration

---

### Tool Contract
**Definition**: Specification defining a tool's interface (name, description, parameters, returns).

**Example**: Calculator tool needs "operation", "a", "b" parameters.

**Related Chapter**: [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md) (Section 2)

---

### Token
**Definition**: Small unit of text (roughly word = 1 token).

**Why**: LLMs charge per token; context windows limit tokens.

**Example**: "Hello world" ~= 2 tokens

**Related Chapter**: [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md) (Token Management)

---

### Troubleshooting
**Definition**: Process of finding and fixing problems.

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md) (Common Troubleshooting section)

**Pro Tip**: Read error messages, Google the error, check documentation.

---

## V

### Vector / Vector Search
**Definition**: Search using mathematical vectors (embeddings).

**Benefit**: Finds semantic similarities, not just keyword matches.

**Example**: Query vector [0.2, 0.8, 0.3] finds documents with similar vectors.

**Related Chapter**: [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md) (Embeddings and Vector Search)

---

### Virtual Environment (venv)
**Definition**: Isolated Python installation for one project.

**Command**: `uv venv` or `python -m venv .venv`

**Why**: Prevents package conflicts between different projects.

**Related Chapter**: [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md): Environment Setup

---

## W

### Workflow
**Definition**: Step-by-step process to accomplish a task.

**Example**: Book-a-flight workflow: get date -> search flights -> select -> book -> confirm.

**Related Chapter**: [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md) (Multi-Step Workflows)

---

## X

### (No common terms starting with X in AI agents)

---

## Y

### YAML
**Definition**: Data format (similar to JSON, more readable).

**Example**:
```yaml
name: Sarah
age: 30
city: Boston
```

---

## Z

### (No common terms starting with Z in AI agents)

---

## Appendix: Terms by Chapter

### [Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md): Environment Setup
- Activation
- Dependencies
- Environment
- Import
- Package
- Package Manager
- Python
- Repository
- Tool
- Virtual Environment

### [Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md): Your First Agent
- Agent
- Async
- Context Window
- LLM
- MockProvider
- Observe-Plan-Act Loop
- Ollama
- OpenAI Provider
- Orchestrator
- Personality
- Provider
- System Prompt

### [Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md): RAG Fundamentals
- Short-Term Memory
- Document Store
- Embedding
- Hallucination
- Knowledge Base
- RAG
- Retriever
- Semantic Search
- Token
- Vector / Vector Search

### [Chapter 4: Tool Integration](../01_beginner/chapter_04_tool_integration.md): Tool Integration
- Flow / Workflow
- Multi-Agent
- Parameter
- Tool
- Tool Contract

### [Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md): Memory and Context
- Short-Term Memory
- Context Window
- JSON
- Long-Term Memory
- Memory
- Storage
- Token

### [Chapter 6: Testing Your Agent](../01_beginner/chapter_06_testing_your_agent.md): Testing
- Integration Test
- Quiz
- Test / Unit Test

### [Chapter 7: Final Project](../01_beginner/chapter_07_final_project.md): Final Project
- Definition of Done
- Definition of Ready
- Glossary
- Hello World / Hello Agent
- Lab
- State Machine
- Troubleshooting
- Workflow

---

## Quick Reference: Most Important Terms

**Tier 1 (Essential)**:
- Agent
- Orchestrator
- Provider
- RAG
- Tool
- Memory
- Embedding

**Tier 2 (Important)**:
- Virtual Environment
- LLM
- Semantic Search
- Token
- Test

**Tier 3 (Helpful to Know)**:
- Hallucination
- Package Manager
- Workflow
- Context Window
- System Prompt

---

**Tip**: Bookmark this page and reference while working through chapters. Return here when you see unfamiliar terms!

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] At least 25 terms included
- [ ] Definitions are concise and beginner-friendly
- [ ] ASCII only

