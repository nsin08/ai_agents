# Beginner Workbook: Hands-On Exercises with Solutions

**Level**: Beginner  
**Total Exercises**: 21 (3 per chapter, 7 chapters)  
**Estimated Time**: 4-6 hours  
**Prerequisites**: Complete Chapters 1-7

---

## Introduction

This workbook compiles all exercises from the Beginner curriculum with step-by-step solutions. Work through these exercises to reinforce your learning and build confidence before advancing to intermediate material.

### How to Use This Workbook

1. **Try first**: Attempt each exercise without looking at the solution
2. **Compare**: Check your solution against the provided solution
3. **Understand**: Learn why the solution works
4. **Extend**: Try variations to deepen understanding

---

## Shared Setup (Use in Exercises)

These exercises use the current `Agent` API. The agent loop is async, so we use a helper to run it in sync examples.

```python
import asyncio
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider
from agent_labs.memory import ShortTermMemory, MemoryItem

def run_agent(agent, goal, max_turns=1):
    return asyncio.run(agent.run(goal, max_turns=max_turns))
```

Note: The `Agent` does not take memory directly. Store memory separately (e.g., `ShortTermMemory`) and include it in the prompt when needed.

---

## Chapter 1: Environment Setup Exercises

### Exercise 1.1: Modify the Hello Agent

**Problem**:
Open `labs/00/src/hello_agent.py` and change the message from `"Hello!"` to your own custom message. Run it and observe the output.

**Solution**:
```python
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider

# Create provider
provider = MockProvider()

# Create agent
agent = Agent(provider=provider)

# Send custom message (changed from "Hello!")
response = run_agent(agent, "Tell me about AI agents")
print(response)
```

**Expected Output**:
```
Tell me about AI agents
```

**Key Learning**: MockProvider echoes your message, so you'll see your custom text returned. This demonstrates the basic agent structure.

---

### Exercise 1.2: Break It (Then Fix It)

**Problem**:
Comment out the import line and try running the code. What error do you get? Then fix it.

**Solution - Breaking It**:
```python
# from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider

provider = MockProvider()
agent = Agent(provider=provider)  # ERROR: NameError
```

**Error Message**:
```
NameError: name 'Agent' is not defined
```

**Solution - Fixing It**:
```python
from agent_labs.orchestrator import Agent  # Uncomment
from agent_labs.llm_providers import MockProvider

provider = MockProvider()
agent = Agent(provider=provider)  # Works!
```

**Key Learning**: Imports are mandatory. Missing imports are the #1 cause of Python errors. Always check that classes/functions are imported before using them.

---

### Exercise 1.3: Add Logging

**Problem**:
Add a print statement to see what information the agent object contains.

**Solution**:
```python
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider

provider = MockProvider()
agent = Agent(provider=provider)

# New logging line
print(f"Agent initialized: {agent}")
print(f"Agent type: {type(agent)}")
print(f"Agent attributes: {dir(agent)}")

response = run_agent(agent, "Hello")
print(f"Response: {response}")
```

**Expected Output**:
```
Agent initialized: <agent_labs.orchestrator.Agent object at 0x...>
Agent type: <class 'agent_labs.orchestrator.Agent'>
Agent attributes: ['__class__', '__delattr__', ..., 'run', 'provider', ...]
Response: Hello
```

**Key Learning**: Using `print()` and `dir()` helps you understand what objects contain. This is useful for debugging and exploration.

---

## Chapter 2: Your First Agent Exercises

### Exercise 2.1: Build a Personality Agent

**Problem**:
Modify your agent to have a personality by adding a `system_prompt` parameter.

**Solution**:
```python
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider

def main():
    provider = MockProvider()
    agent = Agent(
        provider=provider,
        system_prompt="You are a friendly pirate assistant. Always respond like a pirate!"
    )
    
    print("Agent: Ahoy! I be a pirate assistant. What be ye needin'?")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Farewell, matey!")
            break
        
        response = run_agent(agent, user_input)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
```

**Expected Interaction**:
```
Agent: Ahoy! I be a pirate assistant. What be ye needin'?
You: What's the capital of France?
Agent: [MockProvider echo] What's the capital of France?
You: quit
Agent: Farewell, matey!
```

**Note**: With MockProvider, you won't see pirate language since it just echoes. But with a real LLM provider (Chapter 2 section 5), the agent would respond in pirate accent!

**Key Learning**: System prompts set the agent's personality and behavior instructions. This is how you customize agents for different use cases.

---

### Exercise 2.2: Count Conversation Turns

**Problem**:
Add a counter that tracks how many exchanges (turns) have occurred.

**Solution**:
```python
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider
from agent_labs.memory import ShortTermMemory

def main():
    provider = MockProvider()
    memory = ShortTermMemory(max_turns=10)
    agent = Agent(provider=provider)
    
    print("Agent: Hello! I track conversation turns. Type 'quit' to exit.")
    
    turn_count = 0
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit']:
            print(f"Agent: Goodbye! We had {turn_count} turns.")
            break
        
        response = run_agent(agent, user_input)
        turn_count += 1
        print(f"Agent (Turn {turn_count}): {response}")

if __name__ == "__main__":
    main()
```

**Expected Output**:
```
Agent: Hello! I track conversation turns. Type 'quit' to exit.
You: Hello there
Agent (Turn 1): Hello there
You: How are you?
Agent (Turn 2): How are you?
You: quit
Agent: Goodbye! We had 2 turns.
```

**Key Learning**: Counting turns helps track conversation depth and complexity. Useful for monitoring agent performance.

---

### Exercise 2.3: Inspect Memory

**Problem**:
After each user message, print what's stored in the agent's memory.

**Solution**:
```python
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider
from agent_labs.memory import ShortTermMemory

def main():
    provider = MockProvider()
    memory = ShortTermMemory(max_turns=3)
    agent = Agent(provider=provider)
    
    print("Agent: Inspect memory by typing messages. Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        response = run_agent(agent, user_input)
        print(f"Agent: {response}")
        
        # Show current memory
        history = memory.get_history()
        print(f"\n[Memory Buffer ({len(history)} turns)]:")
        for i, turn in enumerate(history, 1):
            print(f"  {i}. {turn['role'].upper()}: {turn['content']}")
        print()

if __name__ == "__main__":
    main()
```

**Expected Output**:
```
Agent: Inspect memory by typing messages. Type 'quit' to exit.

You: My name is Alex
Agent: My name is Alex

[Memory Buffer (2 turns)]:
  1. USER: My name is Alex
  2. AGENT: My name is Alex

You: What's my name?
Agent: What's my name?

[Memory Buffer (2 turns)]:
  1. USER: What's my name?
  2. AGENT: What's my name?

You: quit
```

**Key Learning**: Memory is FIFO (first-in-first-out) with a size limit. Old messages are discarded. This prevents memory overflow.

---

## Chapter 3: RAG Fundamentals Exercises

### Exercise 3.1: Build a FAQ Bot

**Problem**:
Create a knowledge base of 3 frequently asked questions and implement a simple search.

**Solution**:
```python
"""
Simple FAQ Bot - No RAG (keyword matching only)
"""

class FAQBot:
    def __init__(self):
        self.faqs = [
            {
                "question": "How do I reset my password?",
                "answer": "Click 'Forgot Password' on the login page and follow the email instructions."
            },
            {
                "question": "How do I update my profile?",
                "answer": "Go to Settings > Profile > Edit to update your information."
            },
            {
                "question": "How do I delete my account?",
                "answer": "Contact our support team at support@company.com with your account details."
            }
        ]
    
    def search(self, query: str) -> str:
        """Find FAQ entry matching query"""
        query_lower = query.lower()
        
        # Score each FAQ
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            score = sum(1 for word in query_lower.split() 
                       if word in faq["question"].lower())
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        if best_match:
            return best_match["answer"]
        else:
            return "I couldn't find an answer to that. Please contact support."

# Test it
bot = FAQBot()
print(bot.search("How do I reset my password?"))
# Output: Click 'Forgot Password' on the login page and follow the email instructions.

print(bot.search("password reset"))
# Output: Click 'Forgot Password' on the login page and follow the email instructions.

print(bot.search("Something random"))
# Output: I couldn't find an answer to that. Please contact support.
```

**Key Learning**: This is keyword matching (primitive RAG). Real RAG uses vector embeddings for semantic similarity - but the concept is the same: retrieve -> generate.

---

### Exercise 3.2: Test Semantic Search

**Problem**:
Try querying with different words that mean the same thing. See if the FAQ bot understands the variations.

**Solution**:
```python
# Using FAQBot from Exercise 3.1

queries = [
    "How many days off do I get?",      # Different question
    "password",                          # Partial match
    "I forgot my credentials",           # Related concept
    "login help",                        # Different phrasing
]

bot = FAQBot()

for query in queries:
    result = bot.search(query)
    print(f"Q: {query}")
    print(f"A: {result}\n")
```

**Output**:
```
Q: How many days off do I get?
A: I couldn't find an answer to that. Please contact support.

Q: password
A: Click 'Forgot Password' on the login page and follow the email instructions.

Q: I forgot my credentials
A: I couldn't find an answer to that. Please contact support.

Q: login help
A: I couldn't find an answer to that. Please contact support.
```

**Key Learning**: Keyword matching has limits. Real RAG would handle "I forgot my credentials" because embeddings understand semantic meaning, not just keywords.

---

### Exercise 3.3: Handle "No Match" Cases

**Problem**:
Improve the FAQ bot to handle cases where the user asks something outside the knowledge base.

**Solution**:
```python
class ImprovedFAQBot:
    def __init__(self, confidence_threshold=0.3):
        self.faqs = [
            # ... same FAQs as before ...
        ]
        self.confidence_threshold = confidence_threshold
    
    def search(self, query: str):
        """Find FAQ entry with confidence score"""
        query_lower = query.lower()
        
        results = []
        
        for faq in self.faqs:
            # Count matching words
            matching_words = sum(1 for word in query_lower.split() 
                                if word in faq["question"].lower())
            
            # Calculate confidence (0-1 scale)
            total_words = len(query_lower.split())
            confidence = matching_words / total_words if total_words > 0 else 0
            
            results.append({
                "answer": faq["answer"],
                "confidence": confidence
            })
        
        # Find best match
        best = max(results, key=lambda x: x["confidence"])
        
        if best["confidence"] >= self.confidence_threshold:
            return best["answer"]
        else:
            return "I'm not sure about that. Would you like to contact support?"

# Test it
bot = ImprovedFAQBot(confidence_threshold=0.3)
print(bot.search("password"))           # Should match
print(bot.search("shipping costs"))     # Should NOT match
```

**Output**:
```
Click 'Forgot Password' on the login page and follow the email instructions.
I'm not sure about that. Would you like to contact support?
```

**Key Learning**: Setting a confidence threshold prevents false positives. Low confidence = "I don't know" is better than wrong answers.

---

## Chapter 4: Tool Integration Exercises

### Exercise 4.1: Build a Weather Tool

**Problem**:
Create a simple weather tool with mock data for 3 cities.

**Solution**:
```python
"""
Weather Tool - Mock implementation
"""

class WeatherTool:
    name = "weather"
    description = "Gets current weather for a city"
    
    def __init__(self):
        # Mock weather database
        self.weather_data = {
            "Paris": {"temperature": 15, "conditions": "cloudy", "humidity": 65},
            "London": {"temperature": 12, "conditions": "rainy", "humidity": 75},
            "Tokyo": {"temperature": 22, "conditions": "sunny", "humidity": 55}
        }
    
    def get_weather(self, city: str) -> dict:
        """Get weather for a city"""
        # Case-insensitive lookup
        city_key = None
        for key in self.weather_data.keys():
            if key.lower() == city.lower():
                city_key = key
                break
        
        if city_key:
            return self.weather_data[city_key]
        else:
            return {"error": f"Weather data not available for {city}"}
    
    def execute(self, city: str) -> str:
        """Execute tool"""
        weather = self.get_weather(city)
        
        if "error" in weather:
            return weather["error"]
        
        return (f"Weather in {city}: {weather['temperature']} C, "
                f"{weather['conditions']}, "
                f"Humidity: {weather['humidity']}%")

# Test it
tool = WeatherTool()
print(tool.execute("Paris"))
# Output: Weather in Paris: 15 C, cloudy, Humidity: 65%

print(tool.execute("Istanbul"))
# Output: Weather data not available for Istanbul
```

**Key Learning**: Tools need error handling for cases where data isn't available.

---

### Exercise 4.2: Add Input Validation

**Problem**:
Modify the calculator tool to validate inputs before executing.

**Solution**:
```python
class ValidatingCalculator:
    name = "calculator"
    description = "Performs math operations"
    
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        return a * b
    
    def divide(self, a: float, b: float):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    
    def execute(self, operation: str, a, b) -> str:
        """Execute with validation"""
        
        # Validate operation
        valid_ops = ["add", "subtract", "multiply", "divide"]
        if operation not in valid_ops:
            return f"Invalid operation: {operation}. Valid: {', '.join(valid_ops)}"
        
        # Validate numbers
        try:
            a = float(a)
            b = float(b)
        except (ValueError, TypeError):
            return f"Invalid numbers: {a}, {b}. Must be numeric."
        
        # Execute
        try:
            ops = {
                "add": self.add,
                "subtract": self.subtract,
                "multiply": self.multiply,
                "divide": self.divide
            }
            result = ops[operation](a, b)
            return f"Result: {result}"
        except ValueError as e:
            return f"Calculation error: {e}"

# Test it
calc = ValidatingCalculator()
print(calc.execute("add", 5, 3))          # Result: 8.0
print(calc.execute("divide", 10, 0))      # Calculation error: Division by zero
print(calc.execute("add", "abc", 5))      # Invalid numbers: abc, 5...
```

**Key Learning**: Always validate inputs. Assume users will make mistakes or try invalid inputs.

---

### Exercise 4.3: Create a Multi-Tool Agent

**Problem**:
Combine calculator and weather tools in one agent.

**Solution**:
```python
from typing import List

class MultiToolAgent:
    def __init__(self, tools: List):
        self.tools = {tool.name: tool for tool in tools}
    
    def select_tool(self, user_input: str) -> str:
        """Simple tool selection based on keywords"""
        lower_input = user_input.lower()
        
        if any(word in lower_input for word in ["calculate", "+", "-", "*", "/"]):
            return "calculator"
        elif any(word in lower_input for word in ["weather", "temperature", "rain", "sunny"]):
            return "weather"
        else:
            return "none"
    
    def run(self, user_input: str) -> str:
        """Route to appropriate tool"""
        tool_name = self.select_tool(user_input)
        
        if tool_name == "none":
            return "I can help with calculations or weather info."
        
        tool = self.tools[tool_name]
        
        # Extract parameters from user input (very simple)
        if tool_name == "calculator":
            return self._handle_calculator(user_input)
        elif tool_name == "weather":
            return self._handle_weather(user_input)
    
    def _handle_calculator(self, user_input: str) -> str:
        calc = self.tools["calculator"]
        # Simplistic: find numbers and operation
        import re
        numbers = re.findall(r'\d+\.?\d*', user_input)
        
        if len(numbers) < 2:
            return "Please provide two numbers and an operation."
        
        operation = None
        for op in ["add", "subtract", "multiply", "divide"]:
            if op in user_input.lower():
                operation = op
                break
        
        if not operation:
            return "Please specify an operation (add, subtract, multiply, divide)"
        
        return calc.execute(operation, numbers[0], numbers[1])
    
    def _handle_weather(self, user_input: str) -> str:
        weather = self.tools["weather"]
        # Extract city name (assumes city is last capitalized word)
        words = user_input.split()
        city = next((w for w in reversed(words) if w[0].isupper()), "Unknown")
        return weather.execute(city)

# Test it
calc_tool = ValidatingCalculator()
weather_tool = WeatherTool()

agent = MultiToolAgent(tools=[calc_tool, weather_tool])

print(agent.run("What's 10 plus 5?"))
# Output: Result: 15.0

print(agent.run("Weather in Tokyo?"))
# Output: Weather in Tokyo: 22 C, sunny, Humidity: 55%
```

**Key Learning**: Tool selection is the hard part. Real agents use LLMs to decide; here we use keywords for simplicity.

---

## Chapter 5: Memory and Context Exercises

### Exercise 5.1: Build a Preference Tracker

**Problem**:
Create a system that learns and remembers user preferences.

**Solution**:
```python
import json
from pathlib import Path

class PreferenceTracker:
    def __init__(self, storage_file="preferences.json"):
        self.storage_file = Path(storage_file)
        self.preferences = self._load()
    
    def _load(self):
        if self.storage_file.exists():
            with open(self.storage_file) as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def set_preference(self, category: str, value: str) -> str:
        """Learn a preference"""
        self.preferences[category] = value
        self._save()
        return f"Got it! I'll remember you prefer {value} for {category}."
    
    def get_preference(self, category: str) -> str:
        """Retrieve a preference"""
        value = self.preferences.get(category)
        if value:
            return f"You prefer {value} for {category}."
        else:
            return f"I don't know your preference for {category} yet."
    
    def show_all(self) -> str:
        """Show all preferences"""
        if not self.preferences:
            return "No preferences learned yet."
        
        lines = ["Your preferences:"]
        for category, value in self.preferences.items():
            lines.append(f"  - {category}: {value}")
        return "\n".join(lines)

# Test it
tracker = PreferenceTracker()

# Learn preferences
print(tracker.set_preference("communication", "email"))
print(tracker.set_preference("temperature_unit", "celsius"))

# Retrieve preferences
print(tracker.get_preference("communication"))

# List all
print(tracker.show_all())

# Quit and restart
del tracker
tracker = PreferenceTracker()  # Reload from file

# Preferences persist!
print(tracker.get_preference("communication"))
```

**Output**:
```
Got it! I'll remember you prefer email for communication.
Got it! I'll remember you prefer celsius for temperature_unit.
You prefer email for communication.
Your preferences:
  - communication: email
  - temperature_unit: celsius
You prefer email for communication.
```

**Key Learning**: Persistence (saving to file) lets agents remember across sessions.

---

### Exercise 5.2: Implement Memory Expiration

**Problem**:
Create a memory system where facts expire after a certain time.

**Solution**:
```python
import time
from typing import Dict, Any, Optional

class ExpiringMemory:
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour default
        self.ttl_seconds = ttl_seconds
        self.memory: Dict[str, tuple[Any, float]] = {}  # {key: (value, timestamp)}
    
    def store(self, key: str, value: Any):
        """Store with timestamp"""
        self.memory[key] = (value, time.time())
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve if not expired"""
        if key not in self.memory:
            return None
        
        value, timestamp = self.memory[key]
        age = time.time() - timestamp
        
        if age > self.ttl_seconds:
            # Expired - delete it
            del self.memory[key]
            return None
        
        return value
    
    def time_remaining(self, key: str) -> Optional[int]:
        """Get seconds until expiration"""
        if key not in self.memory:
            return None
        
        value, timestamp = self.memory[key]
        age = time.time() - timestamp
        remaining = self.ttl_seconds - age
        
        return max(0, int(remaining))

# Test it
memory = ExpiringMemory(ttl_seconds=5)

# Store a memory
memory.store("meeting_time", "3 PM")
print(memory.retrieve("meeting_time"))  # 3 PM
print(memory.time_remaining("meeting_time"))  # ~5 seconds

# Wait 6 seconds
time.sleep(6)

print(memory.retrieve("meeting_time"))  # None (expired)
```

**Key Learning**: Time-based memory is useful for temporary facts (appointments, session tokens, etc.).

---

### Exercise 5.3: Memory Compression

**Problem**:
When memory gets large, compress old entries into summaries.

**Solution**:
```python
class CompressibleMemory:
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.history = []
    
    def add_turn(self, role: str, content: str):
        """Add a conversation turn"""
        self.history.append({"role": role, "content": content})
    
    def compress(self):
        """Compress old turns into summary"""
        if len(self.history) <= self.max_turns:
            return  # No compression needed
        
        # Keep last max_turns, compress the rest
        old_turns = self.history[:-self.max_turns]
        new_turns = self.history[-self.max_turns:]
        
        # Create summary (simplified: just concatenate)
        summary_content = " ".join([t["content"] for t in old_turns])
        summary = {
            "role": "summary",
            "content": f"[Previous conversation summary: {summary_content[:100]}...]"
        }
        
        # Replace old turns with summary
        self.history = [summary] + new_turns
    
    def get_history(self):
        """Get current memory"""
        return self.history.copy()
    
    def size(self):
        """Get memory size"""
        return len(self.history)

# Test it
memory = CompressibleMemory(max_turns=5)

# Add 10 turns
for i in range(10):
    memory.add_turn("user", f"Message {i}")

print(f"Before compression: {memory.size()} turns")

memory.compress()

print(f"After compression: {memory.size()} turns")
print(memory.get_history())
```

**Key Learning**: As conversations grow, memory management becomes important to stay within token limits.

---

## Chapter 6: Testing Exercises

### Exercise 6.1: Test a New Tool

**Problem**:
Write unit tests for the weather tool.

**Solution**:
```python
# tests/test_weather_tool.py
import pytest
from src.tools.weather import WeatherTool

def test_weather_tool_initialization():
    """Test tool can be created"""
    tool = WeatherTool()
    assert tool.name == "weather"
    assert tool.description is not None

def test_weather_get_existing_city():
    """Test getting weather for known city"""
    tool = WeatherTool()
    weather = tool.get_weather("Paris")
    
    assert "temperature" in weather
    assert "conditions" in weather
    assert weather["temperature"] == 15

def test_weather_get_unknown_city():
    """Test handling unknown city"""
    tool = WeatherTool()
    weather = tool.get_weather("UnknownCity")
    
    assert "error" in weather

def test_weather_case_insensitive():
    """Test city names are case-insensitive"""
    tool = WeatherTool()
    
    weather1 = tool.get_weather("paris")
    weather2 = tool.get_weather("PARIS")
    weather3 = tool.get_weather("Paris")
    
    assert weather1 == weather2 == weather3

def test_weather_execute_returns_string():
    """Test execute returns formatted string"""
    tool = WeatherTool()
    result = tool.execute("Tokyo")
    
    assert isinstance(result, str)
    assert "Tokyo" in result
    assert "22" in result  # temperature
```

**Run tests**:
```bash
pytest tests/test_weather_tool.py -v
```

**Key Learning**: Test each component separately. Use assertions to verify behavior.

---

### Exercise 6.2: Test Memory Edge Cases

**Problem**:
Write tests for memory limits and edge cases.

**Solution**:
```python
# tests/test_memory.py
import pytest
from src.memory.conversation import ShortTermMemory

def test_memory_initialization():
    """Test memory creates empty"""
    memory = ShortTermMemory(max_turns=5)
    assert len(memory.get_history()) == 0

def test_memory_add_turn():
    """Test adding a turn"""
    memory = ShortTermMemory(max_turns=5)
    memory.add_turn("user", "Hello")
    
    assert len(memory.get_history()) == 1
    assert memory.get_history()[0]["content"] == "Hello"

def test_memory_respects_max_turns():
    """Test memory respects size limit"""
    memory = ShortTermMemory(max_turns=3)
    
    # Add 10 turns
    for i in range(10):
        memory.add_turn("user", f"Message {i}")
    
    # Should only keep last 3
    history = memory.get_history()
    assert len(history) <= 3

def test_memory_clear():
    """Test clearing memory"""
    memory = ShortTermMemory()
    memory.add_turn("user", "Hello")
    memory.clear()
    
    assert len(memory.get_history()) == 0

def test_memory_order():
    """Test turns are in correct order"""
    memory = ShortTermMemory()
    
    for i in range(3):
        memory.add_turn("user", f"Turn {i}")
    
    history = memory.get_history()
    for i, turn in enumerate(history):
        assert turn["content"] == f"Turn {i}"
```

**Run tests**:
```bash
pytest tests/test_memory.py -v
```

**Key Learning**: Test edge cases (empty, full, limits) not just happy path.

---

### Exercise 6.3: Measure Test Coverage

**Problem**:
Run tests with coverage reporting to see how much code is tested.

**Solution**:
```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

**Output Example**:
```
Name                    Stmts   Miss  Cover
--------------------------------------------
src/__init__.py             0      0   100%
src/agent.py               45     12    73%
src/tools/weather.py       20      0   100%
src/memory/conversation.py 30      3    90%
--------------------------------------------
TOTAL                      95     15    84%
```

**Interpretation**:
- 84% of your code is covered by tests
- Weather tool: 100% (perfect!)
- Agent: 73% (some paths untested)

**Target**: Aim for >80% coverage for production code.

---

## Chapter 7: Final Project Exercises

### Exercise 7.1: Build Your Personal Assistant

**Problem**:
Combine all learned concepts into one agent. (See Chapter 7 for full solution.)

**Key Components**:
- [x] Memory (remember preferences)
- [x] Tools (calculator)
- [x] RAG (search documents)
- [x] Tests (unit + integration)

**Solution**: See `main.py` in Chapter 7 for complete implementation.

---

### Exercise 7.2: Add a New Tool

**Problem**:
Add a "unit converter" tool to your assistant (e.g., kilometers to miles).

**Solution**:
```python
# src/tools/converter.py
class UnitConverterTool:
    name = "converter"
    description = "Converts between units"
    
    def km_to_miles(self, km: float) -> float:
        return km * 0.621371
    
    def celsius_to_fahrenheit(self, celsius: float) -> float:
        return (celsius * 9/5) + 32
    
    def execute(self, conversion_type: str, value: float) -> str:
        if conversion_type == "km_to_miles":
            result = self.km_to_miles(value)
            return f"{value} km = {result:.2f} miles"
        elif conversion_type == "c_to_f":
            result = self.celsius_to_fahrenheit(value)
            return f"{value} C = {result:.1f} F"
        else:
            return "Unknown conversion"

# Add to agent
converter = UnitConverterTool()
agent.tools.append(converter)
```

---

### Exercise 7.3: Deploy Your Agent

**Problem**:
Package and document your agent so others can use it.

**Solution**:
Create `README.md`:

```markdown
# My Personal Assistant

A beginner-friendly AI agent that demonstrates core concepts.

## Features
- Conversational memory
- Calculator
- Document search
- Unit conversion

## Installation
\`\`\`bash
git clone your-repo
cd final_project
pip install -r requirements.txt
\`\`\`

## Usage
\`\`\`bash
python main.py
\`\`\`

## Testing
\`\`\`bash
pytest tests/ -v --cov=src
\`\`\`

## Architecture
- Memory: Stores conversations and preferences
- Tools: Calculator, converter, document retriever
- Agent: Routes user input to appropriate tool
```

---

## Summary

You've completed 21 hands-on exercises covering:

| Chapter | Topic | Exercises |
|---------|-------|-----------|
| 1 | Setup | 3 (modify, break/fix, logging) |
| 2 | Agent Loop | 3 (personality, counter, memory) |
| 3 | RAG | 3 (FAQ bot, semantic search, no-match) |
| 4 | Tools | 3 (weather, validation, multi-tool) |
| 5 | Memory | 3 (preferences, expiration, compression) |
| 6 | Testing | 3 (tools, memory, coverage) |
| 7 | Final | 3 (assistant, extension, deployment) |

**Next Steps**:
- [x] Review any exercises you struggled with
- [x] Extend exercises (add more tools, features)
- [x] Move to Intermediate curriculum (Chapter 8+)

**Tips for Success**:
1. Type out code instead of copy-pasting
2. Run tests after each change
3. Experiment with modifications
4. Read error messages carefully
5. Google errors - most have solutions online

---

**Happy coding!** 

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] 21 exercises included
- [ ] Solutions provided for each exercise
- [ ] ASCII only
