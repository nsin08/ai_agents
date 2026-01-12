# Chapter 5: Memory and Context

**Level**: Beginner  
**Duration**: 30-45 minutes  
**Prerequisites**: [Chapter 4 - Tool Integration](./chapter_04_tool_integration.md)  
**Lab**: [Lab 4 - Memory Management](../../../labs/04/README.md)

---

## Learning Objectives

By the end of this chapter, you will:

1. **Understand** different types of agent memory (short-term, long-term, episodic)
2. **Implement** conversation memory that persists across sessions
3. **Manage** context windows and token limits
4. **Build** agents that remember user preferences
5. **Design** memory retrieval strategies

---

## 1. Introduction: Why Memory Matters

### The Memory Problem

**Without Memory**:
```
User: My name is Sarah and I live in Boston.
Agent: Nice to meet you!

[5 minutes later]

User: What's the weather where I live?
Agent: I don't know where you live.
```
❌ The agent forgot everything from earlier.

**With Memory**:
```
User: My name is Sarah and I live in Boston.
Agent: Nice to meet you, Sarah!

[5 minutes later]

User: What's the weather where I live?
Agent: Let me check the weather in Boston for you...
```
✅ The agent remembered Sarah's name and location.

---

## 2. Types of Memory

### Short-Term Memory (Conversation Buffer)
**What**: Recent conversation (last few turns)  
**Lifespan**: Current session only  
**Use case**: Maintain context within a conversation

**Example**:
```python
from agent_labs.memory import ConversationMemory

memory = ConversationMemory(max_turns=5)  # Keep last 5 exchanges
memory.add_turn("user", "Hello")
memory.add_turn("agent", "Hi! How can I help?")

print(memory.get_history())
# [{"role": "user", "content": "Hello"}, {"role": "agent", "content": "Hi!..."}]
```

### Long-Term Memory (Persistent Storage)
**What**: Important facts stored permanently  
**Lifespan**: Across sessions (days, weeks, forever)  
**Use case**: User preferences, past interactions

**Example**:
```python
from agent_labs.memory import LongTermMemory

memory = LongTermMemory(storage_path="user_data.json")
memory.store("user_name", "Sarah")
memory.store("user_city", "Boston")

# Later (even after restarting)
name = memory.retrieve("user_name")  # "Sarah"
```

### Episodic Memory (Semantic Search)
**What**: Searchable past conversations  
**Lifespan**: Permanent, but retrieved by relevance  
**Use case**: "What did we discuss about Project X?"

**Example**:
```python
from agent_labs.memory import EpisodicMemory

memory = EpisodicMemory()
memory.add_episode("Discussed vacation policy: 15 days PTO")
memory.add_episode("Talked about remote work: 3 days/week allowed")

# Later: Search by topic
results = memory.search("remote work")
# Returns: "Talked about remote work: 3 days/week allowed"
```

---

## 3. Building a Memory-Enabled Agent

### Step 1: Basic Conversation Memory

Create `labs/04/exercises/memory_agent.py`:

```python
"""
Memory-Enabled Agent - Remembers conversation context
"""
import asyncio
from src.agent_labs.orchestrator import Agent
from src.agent_labs.llm_providers import MockProvider
from src.agent_labs.memory import ConversationMemory

async def main():
    provider = MockProvider()
    memory = ConversationMemory(max_turns=10)
    
    agent = Agent(
        provider=provider,
        memory=memory
    )
    
    print("Agent: Hello! I'm your assistant. I remember our conversation.")
    print("Agent: Type 'history' to see conversation, or 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'history':
            print("\n--- Conversation History ---")
            for turn in memory.get_history():
                print(f"{turn['role'].capitalize()}: {turn['content']}")
            print("----------------------------\n")
            continue
        
        response = await agent.run(user_input, max_turns=1)
        print(f"Agent: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

**Try it**:
```bash
python labs/04/exercises/memory_agent.py
```

**Example interaction**:
```
Agent: Hello! I'm your assistant. I remember our conversation.
You: My name is Sarah
Agent: [MockProvider echo] My name is Sarah

You: What's my name?
Agent: [MockProvider echo] What's my name?

You: history
--- Conversation History ---
User: My name is Sarah
Agent: [MockProvider echo] My name is Sarah
User: What's my name?
Agent: [MockProvider echo] What's my name?
----------------------------
```

### Step 2: Add Persistent Memory

```python
import asyncio
from src.agent_labs.memory import LongTermMemory
import json

async def main():
    provider = MockProvider()
    conversation_memory = ConversationMemory(max_turns=10)
    long_term_memory = LongTermMemory(storage_path="user_profile.json")
    
    agent = Agent(
        provider=provider,
        memory=conversation_memory
    )
    
    print("Agent: Hello! I can remember facts about you permanently.")
    print("Commands: 'save [key] [value]', 'recall [key]', 'quit'\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'quit':
            break
        elif user_input.startswith('save '):
            # Save to long-term memory
            parts = user_input.split(' ', 2)
            if len(parts) == 3:
                key, value = parts[1], parts[2]
                long_term_memory.store(key, value)
                print(f"Agent: Saved {key} = {value}\n")
            continue
        elif user_input.startswith('recall '):
            # Retrieve from long-term memory
            key = user_input.split(' ', 1)[1]
            value = long_term_memory.retrieve(key)
            if value:
                print(f"Agent: {key} = {value}\n")
            else:
                print(f"Agent: I don't have '{key}' in memory.\n")
            continue
        
        response = await agent.run(user_input, max_turns=1)
        print(f"Agent: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

**Try it**:
```
You: save name Sarah
Agent: Saved name = Sarah

You: save city Boston
Agent: Saved city = Boston

[Restart the program]

You: recall name
Agent: name = Sarah

You: recall city
Agent: city = Boston
```

---

## 4. Context Windows and Token Management

### The Token Limit Problem

LLMs have **context windows** (maximum input size):
- GPT-3.5: 4,096 tokens (~3,000 words)
- GPT-4: 8,192 tokens (~6,000 words)
- GPT-4-32k: 32,768 tokens (~24,000 words)

**Problem**: Long conversations exceed limits.

**Solution**: Memory management strategies.

### Strategy 1: Sliding Window
Keep only recent N turns:
```python
memory = ConversationMemory(max_turns=10)  # Only last 10 exchanges
```

### Strategy 2: Summarization
Summarize old conversations:
```python
if len(memory.get_history()) > 20:
    old_messages = memory.get_history()[:10]  # First 10 turns
    summary = agent.summarize(old_messages)
    memory.replace_with_summary(summary)
```

### Strategy 3: Selective Retrieval
Only include relevant past turns:
```python
# Current query: "What's the refund policy?"
# Retrieve: Only turns about refunds (not other topics)
relevant_memory = memory.search_relevant("refund policy", top_k=3)
```

---

## 5. Memory Retrieval Strategies

### When to Retrieve Memory?

**Always** (continuous context):
```python
# Every response includes full conversation history
response = await agent.run(user_input, max_turns=1, context=memory.get_all())
```

**On-Demand** (explicit retrieval):
```python
# Only retrieve when user asks "What did I say about X?"
if "remember" in user_input or "earlier" in user_input:
    relevant = memory.search(user_input)
    response = await agent.run(user_input, max_turns=1, context=relevant)
```

**Semantic Search** (automatic relevance):
```python
# Embed current query, find similar past conversations
query_embedding = embed(user_input)
relevant_past = memory.find_similar(query_embedding, top_k=3)
response = await agent.run(user_input, max_turns=1, context=relevant_past)
```

---

## 6. Hands-On Exercises

### Exercise 1: Build a Preference Tracker

```python
class PreferenceAgent:
    def __init__(self):
        self.preferences = LongTermMemory()
        self.agent = Agent(
            provider=MockProvider(),
            memory=ConversationMemory(max_turns=5)
        )
    
    def learn_preference(self, category, value):
        """Learn user preferences"""
        self.preferences.store(category, value)
        return f"Got it! I'll remember you prefer {value} for {category}."
    
    def get_preference(self, category):
        """Retrieve preference"""
        return self.preferences.retrieve(category)

# Usage
agent = PreferenceAgent()
agent.learn_preference("communication", "email")
agent.learn_preference("temperature_unit", "celsius")

# Later
print(agent.get_preference("communication"))  # "email"
```

### Exercise 2: Implement Memory Expiration

Add timestamps and expiration:

```python
import time

class ExpiringMemory:
    def __init__(self, ttl_seconds=3600):  # 1 hour TTL
        self.memory = {}
        self.ttl = ttl_seconds
    
    def store(self, key, value):
        self.memory[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def retrieve(self, key):
        if key in self.memory:
            age = time.time() - self.memory[key]["timestamp"]
            if age < self.ttl:
                return self.memory[key]["value"]
            else:
                del self.memory[key]  # Expired
        return None
```

### Exercise 3: Memory Compression

Compress memory when it gets too large:

```python
def compress_memory(memory, target_size=5):
    """Keep only most important messages"""
    history = memory.get_history()
    
    if len(history) <= target_size:
        return  # No compression needed
    
    # Strategy: Keep first message + last (target_size - 1) messages
    compressed = [history[0]]  # Keep greeting/context
    compressed.extend(history[-(target_size-1):])  # Keep recent
    
    memory.clear()
    for turn in compressed:
        memory.add_turn(turn["role"], turn["content"])
```

---

## 7. Common Memory Pitfalls

### Pitfall 1: Unbounded Memory Growth
```python
# Bad: Memory grows forever
memory = ConversationMemory(max_turns=None)

# Good: Set reasonable limit
memory = ConversationMemory(max_turns=20)
```

### Pitfall 2: Forgetting Important Context
```python
# Bad: Only keep last 2 turns (too short!)
memory = ConversationMemory(max_turns=2)

# Good: Balance context vs. token limits
memory = ConversationMemory(max_turns=10)
```

### Pitfall 3: Not Persisting Critical Data
```python
# Bad: Lose everything on restart
memory = ConversationMemory()  # RAM only

# Good: Save to disk for important data
memory = LongTermMemory(storage_path="user_data.json")
```

---

## 8. Key Concepts Summary

| Concept | What It Is | When to Use |
|---------|------------|-------------|
| **Short-Term Memory** | Recent conversation turns | Current session context |
| **Long-Term Memory** | Persistent facts | User preferences, profiles |
| **Episodic Memory** | Searchable past conversations | "What did we discuss?" |
| **Context Window** | Max tokens LLM can process | Token management |
| **Sliding Window** | Keep only recent N turns | Prevent overflow |

---

## 9. Glossary

- **Short-Term Memory**: Temporary storage for recent conversation (current session only)
- **Long-Term Memory**: Persistent storage for important facts (across sessions)
- **Episodic Memory**: Searchable historical conversations by semantic similarity
- **Context Window**: Maximum number of tokens (words) an LLM can process at once
- **Token**: Unit of text (roughly 1 word = 1.3 tokens)
- **Sliding Window**: Strategy to keep only recent N conversation turns
- **Memory Compression**: Reducing memory size by summarization or selective removal

---

## 10. What's Next?

✅ **You've completed**: Building memory-enabled agents  
🎯 **Next chapter**: [Chapter 6 - Testing Your Agent](./chapter_06_testing_your_agent.md)  
🔬 **Next lab**: Continue with Lab 4 advanced exercises

### Skills Unlocked
- ✅ Implement conversation memory
- ✅ Build persistent storage for user data
- ✅ Manage context windows and token limits
- ✅ Design memory retrieval strategies
- ✅ Handle memory compression and expiration

### Preview: Chapter 6 (Testing)
In the next chapter, you'll:
- Write unit tests for agent components
- Mock LLM providers for reproducible tests
- Implement integration tests
- Set up CI/CD for automated testing

**The Big Idea**: Memory gives agents continuity. **Testing ensures agents work correctly.**

---

## 11. Self-Assessment Quiz

1. **What's the difference between short-term and long-term memory?**
   - A) Short-term is faster
   - B) Short-term lasts one session, long-term persists across sessions
   - C) There's no difference
   - D) Long-term is more expensive

2. **What's a context window?**
   - A) A GUI element
   - B) Maximum tokens an LLM can process at once
   - C) A type of memory
   - D) A debugging tool

3. **Why limit memory to max_turns?**
   - A) To save disk space
   - B) To prevent token overflow and manage context size
   - C) It makes agents faster
   - D) It's not necessary

4. **What's episodic memory used for?**
   - A) Storing user preferences
   - B) Searchable past conversations by relevance
   - C) Current conversation only
   - D) Error logging

5. **What's a sliding window strategy?**
   - A) GUI animation
   - B) Keep only recent N conversation turns
   - C) A type of tool
   - D) Memory encryption

6. **When should you use long-term memory?**
   - A) For every message
   - B) For important facts that need to persist (user name, preferences)
   - C) Never—short-term is enough
   - D) Only for errors

7. **What happens if memory exceeds context window?**
   - A) Nothing—LLMs handle it
   - B) LLM errors or truncates, losing context
   - C) Agent speeds up
   - D) Memory automatically compresses

8. **What's memory compression?**
   - A) Zipping memory files
   - B) Reducing memory size via summarization or removal
   - C) Encrypting memory
   - D) Not a real technique

9. **How do you persist memory across sessions?**
   - A) Can't be done
   - B) Save to file/database (LongTermMemory)
   - C) LLMs remember automatically
   - D) Use more RAM

10. **What's a good max_turns value for short-term memory?**
    - A) 2 (minimal)
    - B) 10-20 (balanced)
    - C) 1000 (maximum)
    - D) Unlimited

### Answers
1. B, 2. B, 3. B, 4. B, 5. B, 6. B, 7. B, 8. B, 9. B, 10. B

**Scoring**:
- 9-10: Excellent! You understand memory systems deeply.
- 7-8: Good! Review sliding window and compression techniques.
- 5-6: Re-read sections 2-5 and complete all exercises.
- <5: Start over with hands-on exercises—practice makes perfect!

---

## 8. Memory Optimization Strategies

### Token Budget Management
LLMs have hard limits—you must stay under them:

**GPT-4**: 8,192 tokens (standard) or 32,768 tokens (extended)  
**GPT-3.5**: 4,096 tokens (standard) or 16,384 tokens (extended)  
**Claude 3**: 200,000 tokens (massive context window!)

**Calculating token usage**:
```python
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Example:
conversation = memory.get_history()
total_tokens = sum(count_tokens(msg['content']) for msg in conversation)
print(f"Current context: {total_tokens} tokens")

# Set alert threshold
MAX_TOKENS = 6000  # Leave buffer for response
if total_tokens > MAX_TOKENS:
    print("⚠️ Approaching token limit! Consider compression.")
```

### Memory Compression Techniques

**1. Summarization (Best for long conversations)**:
```python
async def compress_memory(memory, agent):
    """Summarize old turns to save tokens"""
    history = memory.get_history()
    
    # Keep recent 5 turns, summarize the rest
    recent = history[-10:]  # Last 5 turns = 10 messages (user + agent)
    old = history[:-10]
    
    if len(old) > 0:
        # Generate summary of old conversation
        old_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in old])
        summary_prompt = f"Summarize this conversation in 2-3 sentences:\n{old_text}"
        summary = await agent.run(summary_prompt, max_turns=1)
        
        # Replace old history with summary
        memory.clear()
        memory.add_message("system", f"Previous conversation summary: {summary}")
        for msg in recent:
            memory.add_message(msg['role'], msg['content'])
```

**2. Entity Extraction (Keep only key facts)**:
```python
def extract_entities(conversation):
    """Extract important entities from conversation"""
    entities = {
        "user_name": None,
        "preferences": [],
        "mentioned_topics": [],
        "decisions_made": []
    }
    
    for msg in conversation:
        content = msg['content'].lower()
        
        # Extract name
        if "my name is" in content:
            entities["user_name"] = content.split("my name is")[-1].strip().split()[0]
        
        # Extract preferences
        if "i prefer" in content or "i like" in content:
            entities["preferences"].append(content)
    
    return entities

# Use entities to create compressed context
entities = extract_entities(memory.get_history())
compressed_context = f"User: {entities['user_name']}. Preferences: {entities['preferences']}"
```

**3. Selective Retention (Keep important turns only)**:
```python
class SmartMemory:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
        self.important_turns = []  # Always keep
        self.regular_turns = []    # Sliding window
        self.max_regular = 10
    
    def add_turn(self, user_msg, agent_msg, is_important=False):
        turn = {"user": user_msg, "agent": agent_msg}
        
        if is_important:
            self.important_turns.append(turn)
        else:
            self.regular_turns.append(turn)
            if len(self.regular_turns) > self.max_regular:
                self.regular_turns.pop(0)  # Remove oldest
    
    def get_context(self):
        """Return all important + recent regular turns"""
        all_turns = self.important_turns + self.regular_turns
        return all_turns
```

### When to Use Which Memory Type

| Scenario | Memory Type | Retention | Example |
|----------|-------------|-----------|---------|
| **Chatbot** | ConversationMemory | Last 10-20 turns | Customer support |
| **Task agent** | EpisodicMemory | Current task only | "Book a flight" |
| **Personal assistant** | LongTermMemory | Permanent | User preferences |
| **Research agent** | VectorMemory | Semantic similarity | "Find similar papers" |
| **Multi-day project** | Hybrid (Short+Long) | Important facts + recent | Code review assistant |

### Real-World Memory Patterns

**Pattern 1: Hybrid Memory (Best for production)**:
```python
class HybridMemoryAgent:
    def __init__(self):
        self.short_term = ConversationMemory(max_turns=10)
        self.long_term = LongTermMemory(storage_path="user_profile.json")
        self.agent = Agent(provider=provider, memory=self.short_term)
    
    async def process_message(self, user_input):
        # Check if user is sharing important info
        if self.is_important(user_input):
            self.save_to_long_term(user_input)
        
        # Add long-term context to current conversation
        user_profile = self.long_term.retrieve("profile")
        context = f"User profile: {user_profile}\n\nRecent conversation:\n"
        
        response = await self.agent.run(user_input, max_turns=1, context=context)
        return response
    
    def is_important(self, text):
        """Determine if message should be permanently stored"""
        keywords = ["my name is", "i prefer", "remember that", "always", "never"]
        return any(keyword in text.lower() for keyword in keywords)
```

**Pattern 2: Automatic Memory Cleanup**:
```python
import asyncio
from datetime import datetime, timedelta

class AutoCleanMemory:
    def __init__(self, ttl_hours=24):
        self.memory = []
        self.ttl = timedelta(hours=ttl_hours)
    
    def add_message(self, role, content):
        self.memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        self.cleanup()  # Remove expired messages
    
    def cleanup(self):
        """Remove messages older than TTL"""
        now = datetime.now()
        self.memory = [
            msg for msg in self.memory
            if now - msg['timestamp'] < self.ttl
        ]
```

### Performance Impact of Memory

**Memory size affects**:
- Response time (more context = slower LLM processing)
- Cost (you pay per token—context + response)
- Quality (too much irrelevant context confuses LLMs)

**Benchmark: Response time vs. context size** (GPT-4):
| Context Size | Response Time | Cost per Call |
|--------------|---------------|---------------|
| 500 tokens | 1.2 seconds | $0.01 |
| 2,000 tokens | 2.5 seconds | $0.04 |
| 6,000 tokens | 5.1 seconds | $0.12 |
| 10,000 tokens | 8.7 seconds | $0.20 |

**Takeaway**: Keep context lean! Compress aggressively.

---

## Further Reading

- [Lab 4 - Memory Management (Full Implementation)](../../../labs/04/README.md)
- [LangChain Memory Documentation](https://python.langchain.com/docs/modules/memory/)
- [OpenAI Token Counting](https://platform.openai.com/tokenizer)

---

**Chapter Complete!** 🎉  
You've learned how to give agents memory and context management!

**Next**: [Chapter 6 - Testing Your Agent →](./chapter_06_testing_your_agent.md)

---

*Estimated reading time: 25 minutes*  
*Hands-on exercises: 15-20 minutes*  
*Total chapter time: 40-45 minutes*
