# Chapter 2: Your First Agent

**Level**: Beginner  
**Duration**: 30-45 minutes  
**Prerequisites**: [Chapter 1 - Environment Setup](./chapter_01_environment_setup.md)  
**Lab**: [Lab 0 - Environment Setup](../../../../labs/00/README.md)

---

## Learning Objectives

By the end of this chapter, you will:

1. **Understand** what makes code an "agent" vs. a simple program
2. **Build** a conversational agent from scratch
3. **Implement** the core agent loop (observe → plan → act)
4. **Add** basic conversation memory
5. **Compare** different LLM providers (Mock, OpenAI, Ollama)

---

## 1. Introduction: What Is an Agent?

### From Programs to Agents

**Traditional Program**:
```
Input → Process → Output
```
You give it data, it runs, it gives you a result. Done.

**AI Agent**:
```
Observe → Plan → Act → Verify → Repeat
```
The agent continuously runs, making decisions, taking actions, and adapting based on what happens.

### The Key Difference

| Traditional Program | AI Agent |
|---------------------|----------|
| Follows fixed logic | Reasons with an LLM |
| One-shot execution | Continuous loop |
| Brittle (breaks on unexpected input) | Adaptive (handles surprises) |
| No memory | Remembers context |
| Direct function calls | Uses tools dynamically |

**Example**:
- **Program**: Calculator app—you click buttons, it computes
- **Agent**: Personal assistant—you say "Schedule a meeting," it figures out how, asks clarifying questions, accesses your calendar, sends invites

---

## 2. The Agent Architecture

Let's build up to a full agent step by step.

### Level 1: Echo Agent (No Intelligence)
```python
def echo_agent(message):
    return f"You said: {message}"

print(echo_agent("Hello"))
# Output: You said: Hello
```

This isn't an agent—it's just a function. No reasoning, no decision-making.

### Level 2: Static Response Agent
```python
def static_agent(message):
    responses = {
        "hello": "Hi there!",
        "bye": "Goodbye!",
        "help": "I can respond to hello, bye, or help."
    }
    return responses.get(message.lower(), "I don't understand.")

print(static_agent("hello"))  # Hi there!
print(static_agent("weather"))  # I don't understand.
```

Still not an agent—just a lookup table. It can't handle anything new.

### Level 3: LLM-Powered Agent (Real Intelligence!)
```python
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider

provider = MockProvider()
agent = AgentOrchestrator(llm_provider=provider)

response = agent.run("What's the weather?")
print(response)
```

**Now it's an agent** because:
- ✅ Uses an LLM to understand and generate responses
- ✅ Can handle any input (not pre-programmed responses)
- ✅ Has an orchestrator managing the loop
- ✅ Can be extended with tools and memory

---

## 3. Building Your First Real Agent

### Step 1: The Basic Agent

Create a new file: `labs/00/exercises/my_first_agent.py`

```python
"""
My First Agent - A simple conversational agent
"""
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider

def main():
    # Create the provider (where responses come from)
    provider = MockProvider()
    
    # Create the agent
    agent = AgentOrchestrator(
        llm_provider=provider,
        agent_name="MyFirstAgent"
    )
    
    # Single interaction
    user_message = "Hello, can you help me?"
    response = agent.run(user_message)
    
    print(f"User: {user_message}")
    print(f"Agent: {response}")

if __name__ == "__main__":
    main()
```

**Run it**:
```bash
python labs/00/exercises/my_first_agent.py
```

**Output** (with MockProvider):
```
User: Hello, can you help me?
Agent: [MockProvider echo] Hello, can you help me?
```

MockProvider just echoes—not very smart, but perfect for testing structure.

### Step 2: Add Conversation Loop

Let's make it interactive:

```python
def main():
    provider = MockProvider()
    agent = AgentOrchestrator(llm_provider=provider)
    
    print("Agent: Hello! I'm your AI assistant. Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye!")
            break
        
        response = agent.run(user_input)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
```

**Try it**:
```
Agent: Hello! I'm your AI assistant. Type 'quit' to exit.
You: What's the capital of France?
Agent: [MockProvider echo] What's the capital of France?
You: quit
Agent: Goodbye!
```

Still echoing, but now it's a real conversation loop!

### Step 3: Add Memory (Context)

Agents need to remember what you've said:

```python
from agent_labs.memory import ConversationMemory

def main():
    provider = MockProvider()
    memory = ConversationMemory(max_turns=5)  # Remember last 5 exchanges
    
    agent = AgentOrchestrator(
        llm_provider=provider,
        memory=memory
    )
    
    print("Agent: Hello! I can remember our conversation. Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit']:
            # Show conversation history before exiting
            print("\nConversation Summary:")
            for turn in memory.get_history():
                print(f"  {turn['role']}: {turn['content']}")
            break
        
        response = agent.run(user_input)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
```

**Key concepts**:
- `ConversationMemory`: Stores turns (user + agent messages)
- `max_turns=5`: Keep last 5 exchanges (prevents memory overflow)
- `memory.get_history()`: Retrieve all stored messages

---

## 4. Understanding the Orchestrator Loop

When you call `agent.run(message)`, here's what happens:

### The Five-Step Loop

```
┌─────────────────────────────────────────────┐
│  1. OBSERVE                                 │
│     ← Receive user input                    │
│     ← Load memory (past conversation)       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  2. PLAN                                    │
│     • What does the user want?              │
│     • Do I need tools? (Chapter 4)          │
│     • What should I say/do?                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  3. ACT                                     │
│     • Generate response (LLM call)          │
│     • Call tools if needed (Chapter 4)      │
│     • Format output                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  4. VERIFY                                  │
│     • Did it work?                          │
│     • Safe? (Chapter 7)                     │
│     • Need to retry?                        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  5. STORE                                   │
│     → Save to memory                        │
│     → Log metrics (Chapter 6)               │
│     → Return response                       │
└─────────────────────────────────────────────┘
```

**Example flow**:
```python
# User says: "What's 2+2?"

# 1. OBSERVE: orchestrator receives "What's 2+2?"
# 2. PLAN: "User wants math. I need a calculator tool."
# 3. ACT: Call calculator tool → get "4"
# 4. VERIFY: "Result looks good, no errors"
# 5. STORE: Save "User: What's 2+2?" and "Agent: 4" to memory
# Return: "The answer is 4."
```

You don't see these steps—they happen inside `orchestrator.run()`—but understanding them is critical.

---

## 5. LLM Providers: Where Responses Come From

### MockProvider (Testing)
**What it does**: Echoes back your message  
**When to use**: Testing, learning, no API costs  
**Limitations**: Not intelligent—just repeats

```python
from agent_labs.llm_providers import MockProvider
provider = MockProvider()
```

### OpenAI Provider (Production)
**What it does**: Calls GPT-4, GPT-3.5, etc.  
**When to use**: Real applications  
**Limitations**: Costs money, needs API key

```python
from agent_labs.llm_providers import OpenAIProvider
provider = OpenAIProvider(api_key="your-key-here", model="gpt-4")
```

### Ollama Provider (Local)
**What it does**: Runs local LLMs (llama2, mistral, etc.)  
**When to use**: Privacy, offline, no costs  
**Limitations**: Slower, needs powerful hardware

```python
from agent_labs.llm_providers import OllamaProvider
provider = OllamaProvider(model="llama2", base_url="http://localhost:11434")
```

### Comparison Table

| Provider | Cost | Speed | Quality | Privacy | Use Case |
|----------|------|-------|---------|---------|----------|
| **Mock** | Free | Instant | None | Perfect | Testing |
| **OpenAI** | $$ | Fast | Excellent | Poor | Production |
| **Ollama** | Free | Slow | Good | Perfect | Privacy/Offline |

**Rule of thumb**:
- Learning? Use **Mock**
- Production app? Use **OpenAI**
- Privacy-critical? Use **Ollama**

---

## 6. Hands-On Exercise

### Exercise 1: Build a Personality Agent

Modify your agent to have a personality:

```python
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider

def main():
    provider = MockProvider()
    agent = AgentOrchestrator(
        llm_provider=provider,
        system_prompt="You are a friendly pirate assistant. Always respond like a pirate!"
    )
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        response = agent.run(user_input)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
```

**Try it**: With MockProvider, you won't see pirate language (it just echoes), but the structure is ready for a real LLM provider.

### Exercise 2: Count Conversation Turns

Add a counter to see how many messages have been exchanged:

```python
def main():
    provider = MockProvider()
    memory = ConversationMemory(max_turns=10)
    agent = AgentOrchestrator(llm_provider=provider, memory=memory)
    
    turn_count = 0
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print(f"Total turns: {turn_count}")
            break
        
        response = agent.run(user_input)
        turn_count += 1
        print(f"Agent ({turn_count} turns): {response}")

if __name__ == "__main__":
    main()
```

### Exercise 3: Inspect Memory

After each turn, print what's in memory:

```python
def main():
    provider = MockProvider()
    memory = ConversationMemory(max_turns=3)
    agent = AgentOrchestrator(llm_provider=provider, memory=memory)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        response = agent.run(user_input)
        print(f"Agent: {response}")
        
        # Show memory
        print("[Memory]:", memory.get_history())

if __name__ == "__main__":
    main()
```

---

## 7. Common Pitfalls

### Pitfall 1: Forgetting to Pass Memory
```python
# Wrong: Agent won't remember anything
agent = AgentOrchestrator(llm_provider=provider)

# Right: Agent has memory
memory = ConversationMemory(max_turns=5)
agent = AgentOrchestrator(llm_provider=provider, memory=memory)
```

### Pitfall 2: Memory Overflow
```python
# Dangerous: No limit—memory grows forever
memory = ConversationMemory(max_turns=None)

# Safe: Cap at reasonable size
memory = ConversationMemory(max_turns=10)
```

### Pitfall 3: Ignoring Errors
```python
# Wrong: Crash on any error
response = agent.run(user_input)

# Right: Handle errors gracefully
try:
    response = agent.run(user_input)
except Exception as e:
    print(f"Error: {e}")
    response = "Sorry, I encountered an error."
```

---

## 8. Key Concepts Summary

| Concept | What It Is | Example |
|---------|------------|---------|
| **Agent Loop** | Observe → Plan → Act → Verify → Store | Core of every agent |
| **Orchestrator** | Manages the agent lifecycle | `AgentOrchestrator` |
| **Provider** | Where LLM responses come from | Mock, OpenAI, Ollama |
| **Memory** | Stores conversation history | `ConversationMemory` |
| **System Prompt** | Instructions for the agent's behavior | "You are a helpful assistant" |

---

## 9. Glossary

- **Orchestrator**: The controller that manages the agent's loop and coordinates components
- **Provider**: Source of LLM responses (API, local model, or mock)
- **Conversation Turn**: One user message + one agent response
- **System Prompt**: Instructions that define the agent's personality and behavior
- **Memory**: Storage for conversation history (enables context awareness)
- **Context**: Information the agent "knows" (from memory and current input)

---

## 10. What's Next?

✅ **You've completed**: Building a conversational agent with memory  
🎯 **Next chapter**: [Chapter 3 - RAG Fundamentals](./chapter_03_rag_fundamentals.md)  
🔬 **Next lab**: [Lab 1 - RAG Fundamentals](../../../../labs/01/README.md)

### Skills Unlocked
- ✅ Understand agent vs. traditional program
- ✅ Build conversational agent with loop
- ✅ Add memory to maintain context
- ✅ Switch between LLM providers
- ✅ Handle errors gracefully

### Preview: Chapter 3 (RAG)
In the next chapter, you'll:
- Understand the "Retrieve → Generate" pattern
- Build a knowledge base with embeddings
- Make agents answer from specific documents
- Compare vector search vs. keyword search

**The Big Idea**: Right now your agent only knows what's in its training data. RAG lets it access YOUR data (documents, databases, APIs) to give accurate, up-to-date answers.

---

## 11. Self-Assessment Quiz

Test your understanding:

1. **What makes code an "agent" instead of a program?**
   - A) It uses Python
   - B) It has a reasoning loop with an LLM
   - C) It has more than 100 lines
   - D) It connects to the internet

2. **What does the orchestrator do?**
   - A) Manages the agent loop (observe → plan → act)
   - B) Stores conversation history
   - C) Generates LLM responses
   - D) Handles errors only

3. **Why do agents need memory?**
   - A) To run faster
   - B) To remember conversation context
   - C) To reduce API costs
   - D) It's optional and not important

4. **What does MockProvider do?**
   - A) Calls GPT-4
   - B) Echoes back messages for testing
   - C) Runs local LLMs
   - D) Stores conversation history

5. **What's the correct order of the agent loop?**
   - A) Act → Plan → Observe → Verify
   - B) Observe → Plan → Act → Verify
   - C) Plan → Act → Observe → Store
   - D) Verify → Act → Plan → Observe

6. **When should you use MockProvider?**
   - A) Always—it's the best
   - B) For testing and learning (no API costs)
   - C) For production apps
   - D) Only on Fridays

7. **What happens if you don't set `max_turns` on memory?**
   - A) Agent won't work
   - B) Memory grows forever (potential overflow)
   - C) Agent forgets everything immediately
   - D) Nothing—it's not important

8. **What's a "conversation turn"?**
   - A) One user message only
   - B) One agent response only
   - C) One user message + one agent response
   - D) The entire conversation

9. **What's a system prompt?**
   - A) Error message
   - B) Instructions that define agent behavior
   - C) User's input
   - D) Agent's response

10. **Why would you choose Ollama over OpenAI?**
    - A) It's faster
    - B) It's free and runs locally (privacy)
    - C) It has better quality
    - D) It's easier to set up

### Answers
1. B, 2. A, 3. B, 4. B, 5. B, 6. B, 7. B, 8. C, 9. B, 10. B

**Scoring**:
- 9-10: Excellent! You understand agent architecture.
- 7-8: Good! Review the agent loop section.
- 5-6: Re-read the orchestrator and memory sections.
- <5: No worries! Review the code examples and try the exercises.

---

## Further Reading

- [Lab 0 - Environment Setup](../../../../labs/00/README.md)
- [AgentOrchestrator Source Code](../../../../src/agent_labs/orchestrator/)
- [Memory Module Documentation](../../../../src/agent_labs/memory/)
- [LLM Provider Comparison](https://docs.anthropic.com/claude/docs/intro-to-claude)

---

**Chapter Complete!** 🎉  
You've built a real conversational agent with memory. Now let's give it knowledge with RAG!

**Next**: [Chapter 3 - RAG Fundamentals →](./chapter_03_rag_fundamentals.md)

---

*Estimated reading time: 25 minutes*  
*Hands-on exercises: 20 minutes*  
*Total chapter time: 45 minutes*
