# Interactive Agent Scripts

Three interactive scripts for experimenting with AI agents from `src/agent_labs`.

Note: These are test scripts for agent behavior and learning workflows.

## Quick Start (30 seconds)

```bash
# Option 1: Single prompt (fastest)
python scripts/quick_test.py "What is Python?"

# Option 2: Interactive REPL (best for exploration)
python scripts/interactive_agent.py

# Option 3: Learning scenarios
python scripts/explore.py quickstart
```

---

## Scripts Overview

| Script | Purpose | Best For |
|--------|---------|----------|
| **quick_test.py** | Single-prompt testing | Fast verification, CI/CD, one-liners |
| **interactive_agent.py** | Full REPL interface | Deep exploration, conversations, debugging |
| **explore.py** | Predefined scenarios | Structured learning, teaching, demos |

---

## 1. quick_test.py - One-Liner Testing

**Usage:**
```bash
python scripts/quick_test.py "Your prompt here"
```

**Options:**
```bash
python scripts/quick_test.py "Prompt" --ollama           # Use Ollama (requires ollama serve)
python scripts/quick_test.py "Prompt" --model mistral    # Change model
python scripts/quick_test.py "Prompt" --turns 5          # More reasoning iterations
```

**Examples:**
```bash
python scripts/quick_test.py "What is machine learning?"
python scripts/quick_test.py "2+2=?" --ollama --model mistral
python scripts/quick_test.py "I'm thinking of a number between 1-100. It's even, divisible by 3, and less than 50. What could it be?" --turns 5
```

**Pros:** Instant (MockProvider default), single command, perfect for automation/scripts  
**Cons:** Limited interaction, must restart for each prompt

---

## 2. interactive_agent.py - REPL Interface

**Start REPL:**
```bash
python scripts/interactive_agent.py
```

**Interactive Commands:**

| Command | Example | Effect |
|---------|---------|--------|
| Ask question | `> What is AI?` | Run agent with prompt |
| `/help` | `> /help` | Show help menu |
| `/config` | `> /config` | Display configuration |
| `/reset` | `> /reset` | Clear history, restart |
| `/provider TYPE` | `> /provider ollama` | Switch to mock or ollama |
| `/model NAME` | `> /model mistral` | Set model (for ollama) |
| `/max_turns N` | `> /max_turns 5` | Set reasoning iterations (1-10) |
| `/tools` | `> /tools` | List available tools and usage |
| `/summarize TEXT` | `> /summarize Long text here...` | Summarize text (min 50 chars) |
| `/analyze CODE` | `> /analyze def foo(): pass` | Analyze code quality/security/performance |
| `/history` | `> /history` | Show conversation history |
| `/exit` | `> /exit` | Quit |

**Example Session:**
```
> /provider ollama
 Switched to ollama provider

> Hi, my name is Neeraj
 Agent thinking...
[Agent responds and remembers your name]

> What is 2+2?
 Agent thinking...
The answer is 4.

> Do you remember my name?
 Agent thinking...
Yes, your name is Neeraj.

> /history
[Shows full conversation]

> /exit
 Goodbye!
```

**Features:** Conversation memory (context injection), provider switching, full history tracking, real-time feedback, integrated tool support  
**Pros:** Full conversation history, command-driven interface, memory across turns, real tools for text and code analysis  
**Cons:** Requires interactive terminal, OllamaProvider needs Ollama running

---

### Tool Integration

The interactive agent now includes real tools for practical tasks:

#### 1. Text Summarizer Tool

Summarize long text passages (minimum 50 characters):

```bash
python scripts/interactive_agent.py
> /tools
[Shows available tools and usage]

> /summarize The quick brown fox jumps over the lazy dog. This is a longer sentence to make it over 50 characters minimum.
Tool executing: TextSummarizer...
Summary: Fast fox leaps over lazy dog.
```

**Use Cases:**
- Compress long documents
- Extract key points from articles
- Summarize meeting notes
- Condense long descriptions

#### 2. Code Analyzer Tool

Analyze Python code for quality, security, or performance issues:

```bash
> /analyze def slow_function(items):
>     for i in range(len(items)):
>         for j in range(len(items)):
>             if items[i] == items[j]:
>                 pass
> /analyze CODE quality

Tool executing: CodeAnalyzer...
Analysis Results:
- Nested loop complexity: O(n²) - inefficient for large lists
- Suggestion: Use set for O(n) lookup
- Performance: 🔴 Poor - optimize loops
```

**Analysis Types:**
- `quality` - Code style, readability, best practices
- `security` - Potential vulnerabilities, safe practices
- `performance` - Algorithmic complexity, optimization opportunities

**Use Cases:**
- Review code before commit
- Identify performance bottlenecks
- Security audit of user input handling
- Learn optimization patterns

#### Example Tool Session

```bash
> /provider ollama
Switched to ollama provider

> /model mistral
Changed model to: mistral

> /tools
Available Tools:
  - text_summarizer: Summarize long text passages
  - code_analyzer: Analyze code for quality/security/performance

> /summarize Artificial intelligence is transforming industries. Machine learning enables computers to learn from data. Deep learning uses neural networks with multiple layers. NLP processes human language. AI applications span healthcare, finance, and robotics.
Tool executing: TextSummarizer...
Summary: AI transforms industries through ML and DL, enabling language processing across healthcare, finance, and robotics.

> /analyze def process_data(data, threshold=10):
>     result = []
>     for item in data:
>         if item > threshold:
>             result.append(item * 2)
>     return result
Tool executing: CodeAnalyzer...
Code Analysis (quality):
- Readability: ✅ Good - clear logic
- Style: ✅ Follows conventions
- Performance: ✅ O(n) - efficient

> /exit
Goodbye!
```

---

**Pros:** Full conversation history, command-driven interface, memory across turns, integrated tools  
**Cons:** Requires interactive terminal, OllamaProvider needs Ollama running

---

## 3. explore.py - Predefined Scenarios

**Usage:**
```bash
python scripts/explore.py SCENARIO_NAME
```

**Available Scenarios:**
```bash
python scripts/explore.py quickstart     # Simple 2-3 question intro
python scripts/explore.py reasoning      # Logic puzzles and riddles
python scripts/explore.py storytelling   # Creative writing prompts
python scripts/explore.py teaching       # Topic explanations
python scripts/explore.py advanced       # Complex multi-turn reasoning
```

**Features:** Structured learning paths, batch prompts, great for demos/teaching  
**Pros:** No configuration needed, good for learning, reproducible  
**Cons:** Limited to predefined scenarios

---

## Examples: Agent Multi-Stage Reasoning

These examples showcase agent thinking through multiple stages:

### 1. Logic Puzzle - Constraint-Based Reasoning
```bash
python scripts/quick_test.py "I'm thinking of a number between 1-100. It's even, divisible by 3, and less than 50. What could it be?"
```
**Agent Stages:** Parse constraints  Filter by even  Filter by divisible by 3  Filter by < 50  List candidates  Verify answers

### 2. Planning & Execution - Structured Study Plan
```bash
python scripts/interactive_agent.py
> /provider ollama
> I want to learn Python in 30 days. Create a structured study plan with daily goals and milestones.
> /max_turns 5
```
**Agent Stages:** Analyze requirements  Break into weeks  Design daily topics  Set milestones  Create deliverables

### 3. Technical Deep Dive - Mathematical Explanation
```bash
python scripts/quick_test.py "Explain how neural networks learn using backpropagation. Include the forward pass, loss calculation, and gradient descent." --turns 5
```
**Agent Stages:** Explain architecture  Show forward pass  Explain loss function  Describe gradient descent  Detail backpropagation  Provide example

### 4. Creative Task with Constraints - Poetry
```bash
python scripts/quick_test.py "Write a haiku about AI that must include these words: 'learning', 'wonder', 'code'. Verify it follows 5-7-5 syllable structure."
```
**Agent Stages:** Understand haiku structure  Identify word constraints  Generate lines  Count syllables  Verify word inclusion  Refine

### 5. Conversational Memory - Multi-Turn Story
```bash
python scripts/interactive_agent.py
> /provider ollama
> My favorite color is blue, favorite animal is penguin, and lucky number is 7.
> Tell me a creative story combining all three elements.
> Now recommend a perfect gift based on what you know about me.
> /history
```
**Agent Stages:** Extract preferences from first message  Remember context  Generate coherent story  Apply memory to recommendation  Show full history

### 6. Analytical Comparison - Multi-Factor Analysis
```bash
python scripts/quick_test.py "Create a detailed comparison matrix for remote work vs office work. Include: productivity, collaboration, cost, work-life balance, career growth, and flexibility. Use a 1-10 scoring system." --turns 5
```
**Agent Stages:** Identify all factors  Analyze each factor  Establish scoring criteria  Apply weights  Generate comparison matrix  Draw conclusions

### 7. Problem Diagnosis - Root Cause Analysis
```bash
python scripts/quick_test.py "My Python script is slow with 1M row CSV files. It: 1) loads entire CSV, 2) filters by date range, 3) groups by category, 4) sorts by value. Find bottlenecks and suggest optimizations with code." --turns 5
```
**Agent Stages:** Map data flow  Identify operations  Analyze complexity  Find bottlenecks  Propose optimizations  Rank by impact  Provide code

### 8. Code Review & Refactoring - Complex Code Analysis
```bash
python scripts/interactive_agent.py
> /provider ollama
> Review this code for issues:
> def process(data):
>     result = []
>     for i in range(len(data)):
>         for j in range(len(data)):
>             if data[i] == data[j] and i != j:
>                 result.append((i,j))
>     return result
> What's wrong and how to fix it?
> /max_turns 5
```
**Agent Stages:** Understand algorithm  Identify inefficiencies  Detect bugs  Propose fixes  Suggest improvements  Provide refactored code

### 9. Ethical Reasoning - Multi-Perspective Analysis
```bash
python scripts/quick_test.py "Should companies collect user data for AI training? Present arguments from: user privacy advocates, AI researchers, business leaders, and regulators. Then provide a balanced recommendation." --turns 5
```
**Agent Stages:** Identify stakeholders  Present each perspective  Analyze trade-offs  Weigh pros/cons  Draw balanced conclusion

### 10. Systems Design - Architecture Planning
```bash
python scripts/interactive_agent.py
> /provider ollama
> Design a recommendation system for an e-commerce platform handling 10M daily users. Consider: scalability, latency, accuracy, cost, maintenance.
> /max_turns 5
```
**Agent Stages:** Understand requirements  Identify constraints  Propose architecture  Analyze trade-offs  Optimize for each dimension  Provide implementation roadmap

---

## Setup & Configuration

### Using Ollama (Optional for Real LLM)

> **Recommended Model:** `mistral:7b` - Fast, high-quality reasoning, optimized for Labs 1+

1. **Install Ollama**: https://ollama.ai
2. **Start Ollama server**: 
   ```bash
   ollama serve
   ```
3. **Pull a model** (one-time, ~4GB each):
   ```bash
   ollama pull mistral      # Recommended (fast, high quality)
   ollama pull llama2       # Alternative (larger, slower)
   ```
4. **Use in scripts**:
   ```bash
   python scripts/interactive_agent.py
   > /provider ollama
   > /model mistral         # Use recommended model
   > Your prompt here
   ```

**Model Comparison:**

| Model | Speed | Quality | Size | Best For |
|-------|-------|---------|------|----------|
| MockProvider (default) | Instant | N/A | None | Rapid testing, CI/CD |
| **mistral:7b** | ⚡ Fast | ⭐⭐⭐⭐ | 4GB | **Lab 1+ (Recommended)** |
| llama2:7b | Moderate | ⭐⭐⭐ | 4GB | Learning, comparison |
| llama2:13b | Slow | ⭐⭐⭐⭐ | 7GB | Complex reasoning |

### Environment Variables

```bash
# Set Ollama server URL (if not localhost:11434)
$env:OLLAMA_BASE_URL="http://localhost:11434"
```

---

## Common Scenarios

| Scenario | Command | Purpose |
|----------|---------|---------|
| Quick test (instant) | `python scripts/quick_test.py "test prompt"` | Fast feedback with MockProvider |
| Real LLM testing | `python scripts/quick_test.py "prompt" --ollama` | Use actual LLM via Ollama |
| Interactive conversation | `python scripts/interactive_agent.py` | Full REPL with memory |
| With provider switching | `python scripts/interactive_agent.py` then `/provider ollama` | Switch between mock/ollama |
| Complex reasoning | `python scripts/quick_test.py "prompt" --turns 5` | More reasoning iterations |
| Structured learning | `python scripts/explore.py storytelling` | Predefined scenarios |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named agent_labs` | Run from workspace root: `cd d:\wsl_shared\src\ai_agents` |
| `OllamaProvider connection error` | Start Ollama: `ollama serve` in another terminal |
| `Model not found` | Pull model: `ollama pull llama2` |
| Script hangs with Ollama | Check Ollama is running: `ollama list` or `curl http://localhost:11434` |
| Slow response | MockProvider is instant; Ollama depends on model and hardware |

---

## Files in This Directory

- `quick_test.py` - Single-prompt testing script
- `interactive_agent.py` - Full REPL with commands and memory
- `explore.py` - Predefined learning scenarios
- `memory_test.py` - Memory/context injection verification
- `README.md` - This file

---

## Next Steps

1. Try `quick_test.py` with simple prompts first
2. Switch to `interactive_agent.py` for exploration
3. Experiment with multi-stage examples above
4. Use `/provider ollama` for real LLM responses
5. Check `/history` to see how agent uses memory
6. Explore the agent source in `src/agent_labs/`
