# Chapter 4: Tool Integration

**Level**: Beginner  
**Duration**: 30-45 minutes  
**Prerequisites**: [Chapter 3 - RAG Fundamentals](./chapter_03_rag_fundamentals.md)  
**Lab**: [Lab 2 - Tool Integration](../../../labs/02/README.md)

---

## Learning Objectives

By the end of this chapter, you will:

1. **Understand** what tools are and why agents need them
2. **Build** your first agent tool (calculator, API caller)
3. **Implement** tool selection logic (when to use which tool)
4. **Handle** tool errors and validation
5. **Create** multi-step workflows with tools

---

## 1. Introduction: Why Tools Matter

### From Knowledge to Action

**Chapter 3 (RAG)**: Gave agents **knowledge**—they can answer questions from documents.  
**Chapter 4 (Tools)**: Gives agents **power**—they can take **actions**.

**Example**:
- **Without tools**: "User wants to know the weather." → Agent says "I can't check the weather."
- **With tools**: "User wants to know the weather." → Agent calls WeatherAPI tool → Returns "72°F, sunny"

### The Tool Contract

A tool is just a function with:
1. **Name**: What it's called (`get_weather`)
2. **Description**: What it does ("Fetches current weather for a city")
3. **Parameters**: What it needs (`city: string`)
4. **Returns**: What it gives back (`temperature, conditions`)

**Example tool**:
```python
def get_weather(city: str) -> dict:
    """Fetches current weather for a city."""
    # In real code: call weather API
    return {"temperature": 72, "conditions": "sunny"}
```

---

## 2. Types of Tools

### 1. Information Retrieval
**What**: Read-only access to data  
**Examples**: RAG retriever, database queries, API lookups  
**Risk**: Low (can't break anything)

### 2. Calculations
**What**: Math, data processing  
**Examples**: Calculator, statistics, unit conversion  
**Risk**: None (pure functions)

### 3. System Actions
**What**: Change state (write, delete, send)  
**Examples**: Send email, create file, update database  
**Risk**: HIGH (can break things, needs safety—Chapter 7)

### 4. External APIs
**What**: Call third-party services  
**Examples**: Weather, stock prices, flight info  
**Risk**: Medium (costs money, rate limits)

---

## 3. Building Your First Tool

### Step 1: Create a Calculator Tool

Create `labs/02/exercises/calculator_tool.py`:

```python
"""
Calculator Tool - Simple math operations
"""
from typing import Union

class CalculatorTool:
    """A simple calculator tool for agents"""
    
    name = "calculator"
    description = "Performs basic math operations: add, subtract, multiply, divide"
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers"""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a"""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers"""
        return a * b
    
    def divide(self, a: float, b: float) -> Union[float, str]:
        """Divide a by b"""
        if b == 0:
            return "Error: Division by zero"
        return a / b
    
    def execute(self, operation: str, a: float, b: float) -> Union[float, str]:
        """Execute a calculation"""
        operations = {
            "add": self.add,
            "subtract": self.subtract,
            "multiply": self.multiply,
            "divide": self.divide
        }
        
        if operation not in operations:
            return f"Error: Unknown operation '{operation}'"
        
        return operations[operation](a, b)

# Test it
if __name__ == "__main__":
    calc = CalculatorTool()
    print(calc.execute("add", 5, 3))         # 8.0
    print(calc.execute("multiply", 4, 7))    # 28.0
    print(calc.execute("divide", 10, 0))     # Error: Division by zero
```

**Run it**:
```bash
python labs/02/exercises/calculator_tool.py
```

### Step 2: Integrate Tool with Agent

```python
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider
from labs.02.exercises.calculator_tool import CalculatorTool

def main():
    provider = MockProvider()
    calc_tool = CalculatorTool()
    
    agent = AgentOrchestrator(
        llm_provider=provider,
        tools=[calc_tool]
    )
    
    # Agent now has access to calculator!
    response = agent.run("What's 25 * 4?")
    print(response)

if __name__ == "__main__":
    main()
```

---

## 4. Tool Selection: Choosing the Right Tool

### The Selection Process

```
User: "What's the weather in Paris?"

Agent thinks:
1. Parse intent: User wants weather info
2. Check available tools: [calculator, weather_api, database]
3. Select tool: weather_api (best match)
4. Extract parameters: city="Paris"
5. Execute: weather_api.get_weather("Paris")
6. Format response: "It's 15°C and cloudy in Paris."
```

### Implementation Pattern

```python
class AgentWithTools:
    def __init__(self, tools):
        self.tools = {tool.name: tool for tool in tools}
    
    def select_tool(self, user_intent: str) -> str:
        """Select appropriate tool based on intent"""
        # In real agents: LLM decides which tool to use
        # For now: simple keyword matching
        
        if "calculate" in user_intent or any(op in user_intent for op in ["+", "-", "*", "/"]):
            return "calculator"
        elif "weather" in user_intent:
            return "weather_api"
        elif "search" in user_intent:
            return "web_search"
        else:
            return None  # No tool needed
    
    def run(self, user_input: str):
        tool_name = self.select_tool(user_input)
        
        if tool_name:
            tool = self.tools[tool_name]
            result = tool.execute(user_input)
            return f"Used {tool_name}: {result}"
        else:
            return "No tool needed for this query."
```

---

## 5. Multi-Step Workflows

### Example: Book a Flight

**User**: "Book me a flight from NYC to LA next Friday"

**Agent workflow**:
```
Step 1: Use "calendar_tool" to find next Friday's date
  → Returns: "2026-01-17"

Step 2: Use "flight_search_tool" to find flights
  Parameters: origin="NYC", destination="LA", date="2026-01-17"
  → Returns: [Flight 123 @ $250, Flight 456 @ $300]

Step 3: Use "flight_booking_tool" to book cheapest option
  Parameters: flight_id="123", date="2026-01-17"
  → Returns: "Booking confirmed: Flight 123"

Step 4: Use "email_tool" to send confirmation
  Parameters: to="user@example.com", subject="Flight Booked"
  → Returns: "Email sent"

Agent responds: "I've booked you on Flight 123 from NYC to LA on 
                 January 17th for $250. Confirmation sent to your email."
```

### Code Pattern

```python
def book_flight_workflow(agent, user_request):
    # Step 1: Parse request
    details = agent.parse_flight_request(user_request)
    
    # Step 2: Find date
    date = agent.tools["calendar"].get_date(details["when"])
    
    # Step 3: Search flights
    flights = agent.tools["flight_search"].search(
        origin=details["from"],
        destination=details["to"],
        date=date
    )
    
    # Step 4: Select best option
    best_flight = min(flights, key=lambda f: f["price"])
    
    # Step 5: Book it
    confirmation = agent.tools["flight_booking"].book(best_flight)
    
    # Step 6: Notify user
    agent.tools["email"].send(
        to=details["user_email"],
        subject="Flight Booked",
        body=confirmation
    )
    
    return confirmation
```

---

## 6. Hands-On Exercises

### Exercise 1: Build a Weather Tool

```python
class WeatherTool:
    name = "weather"
    description = "Gets current weather for a city"
    
    def get_weather(self, city: str) -> dict:
        # Mock data (in real code: call API)
        weather_data = {
            "Paris": {"temp": 15, "conditions": "cloudy"},
            "London": {"temp": 12, "conditions": "rainy"},
            "Tokyo": {"temp": 22, "conditions": "sunny"}
        }
        return weather_data.get(city, {"temp": "unknown", "conditions": "unknown"})
    
    def execute(self, city: str) -> str:
        weather = self.get_weather(city)
        return f"It's {weather['temp']}°C and {weather['conditions']} in {city}."

# Test it
tool = WeatherTool()
print(tool.execute("Paris"))  # It's 15°C and cloudy in Paris.
```

### Exercise 2: Add Input Validation

Modify the calculator to validate inputs:

```python
def execute(self, operation: str, a: float, b: float):
    # Validate operation
    if operation not in ["add", "subtract", "multiply", "divide"]:
        return f"Error: '{operation}' is not a valid operation"
    
    # Validate numbers
    try:
        a = float(a)
        b = float(b)
    except (ValueError, TypeError):
        return "Error: Invalid numbers provided"
    
    # Execute
    return operations[operation](a, b)
```

### Exercise 3: Create a Multi-Tool Agent

Combine calculator and weather:

```python
calc_tool = CalculatorTool()
weather_tool = WeatherTool()

agent = AgentOrchestrator(
    llm_provider=MockProvider(),
    tools=[calc_tool, weather_tool]
)

# Agent can now do math AND check weather!
agent.run("What's 10 + 5?")          # Uses calculator
agent.run("Weather in Tokyo?")        # Uses weather
```

---

## 7. Error Handling and Safety

### Common Tool Errors

**1. Missing Parameters**
```python
# Bad: weather_tool.execute()  # Missing 'city'
# Good: Validate before execution
if not city:
    return "Error: City parameter is required"
```

**2. Invalid Values**
```python
# Bad: calculator.divide(10, 0)
# Good: Check for division by zero
if operation == "divide" and b == 0:
    return "Error: Cannot divide by zero"
```

**3. API Failures**
```python
try:
    response = requests.get(weather_api_url)
    response.raise_for_status()
except requests.RequestException as e:
    return f"Error: Weather API unavailable - {e}"
```

### Safety Checklist

- ✅ Validate all inputs before execution
- ✅ Handle errors gracefully (don't crash)
- ✅ Set timeouts for external calls
- ✅ Rate limit expensive operations
- ✅ Log tool executions for debugging
- ✅ Require confirmation for dangerous actions (delete, send money)

---

## 8. Key Concepts Summary

| Concept | What It Is | Example |
|---------|------------|---------|
| **Tool** | Function an agent can call | calculator, weather API |
| **Tool Contract** | Name, description, parameters, returns | Defines what tool does |
| **Tool Selection** | Choosing which tool to use | "weather" query → use weather tool |
| **Multi-Step Workflow** | Chaining tools together | Search → filter → book → confirm |
| **Input Validation** | Checking parameters before execution | Reject negative ages |

---

## 9. Glossary

- **Tool**: Function that agents can invoke to perform actions
- **Tool Contract**: Specification of tool's name, description, parameters, and return type
- **Tool Selection**: Process of choosing appropriate tool for a task
- **Parameters**: Inputs required by a tool function
- **Validation**: Checking inputs are correct before execution
- **Multi-Step Workflow**: Sequence of tool calls to accomplish complex task

---

## 10. What's Next?

✅ **You've completed**: Building and integrating tools  
🎯 **Next chapter**: [Chapter 5 - Memory and Context](./chapter_05_memory_and_context.md)  
🔬 **Next lab**: [Lab 4 - Memory Management](../../../labs/04/README.md)

### Skills Unlocked
- ✅ Create agent tools from scratch
- ✅ Implement tool selection logic
- ✅ Handle errors and validate inputs
- ✅ Build multi-step workflows
- ✅ Integrate external APIs

### Preview: Chapter 5 (Memory)
In the next chapter, you'll:
- Understand different types of memory (short-term, long-term, episodic)
- Implement conversation memory that persists across sessions
- Learn about context windows and token management
- Build agents that remember user preferences

**The Big Idea**: Tools give agents power. **Memory gives agents continuity.**

---

## 11. Self-Assessment Quiz

1. **What is a tool in agent terminology?**
   - A) A function the agent can call to perform actions
   - B) A debugging utility
   - C) An LLM provider
   - D) A database

2. **What are the four parts of a tool contract?**
   - A) Name, price, color, size
   - B) Name, description, parameters, returns
   - C) Input, output, error, log
   - D) Tool, agent, user, system

3. **Which type of tool has the highest risk?**
   - A) Calculator (pure function)
   - B) Information retrieval (read-only)
   - C) System actions (write, delete, send)
   - D) All tools are equally safe

4. **What should you do before executing a tool?**
   - A) Nothing—just run it
   - B) Validate inputs and handle errors
   - C) Always ask user for confirmation
   - D) Log to database

5. **What's a multi-step workflow?**
   - A) Running one tool multiple times
   - B) Chaining tools together to accomplish complex tasks
   - C) Using multiple agents
   - D) A type of memory

6. **How does tool selection work?**
   - A) Agent randomly picks a tool
   - B) Agent analyzes intent and picks appropriate tool
   - C) User always specifies which tool
   - D) Tools are executed in order

7. **What happens if a tool receives invalid parameters?**
   - A) Agent crashes
   - B) Tool should return error message gracefully
   - C) Nothing—tools always work
   - D) User gets banned

8. **When should you require user confirmation?**
   - A) For all tools
   - B) For dangerous actions (delete, send money)
   - C) Never—automate everything
   - D) Only on Tuesdays

9. **What's the benefit of tools over hardcoded logic?**
   - A) Tools are slower
   - B) Agents can dynamically choose and combine tools
   - C) No benefit—hardcoded is better
   - D) Tools use less memory

10. **What should you do when an external API fails?**
    - A) Crash the agent
    - B) Return error message and fallback gracefully
    - C) Retry infinitely
    - D) Ignore the error

### Answers
1. A, 2. B, 3. C, 4. B, 5. B, 6. B, 7. B, 8. B, 9. B, 10. B

---

## Further Reading

- [Lab 2 - Tool Integration (Full Implementation)](../../../labs/02/README.md)
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/agents/tools/)
- [Function Calling with OpenAI](https://platform.openai.com/docs/guides/function-calling)

---

**Chapter Complete!** 🎉  
You've learned how to give agents the power to take actions with tools!

**Next**: [Chapter 5 - Memory and Context →](./chapter_05_memory_and_context.md)

---

*Estimated reading time: 25 minutes*  
*Hands-on exercises: 20 minutes*  
*Total chapter time: 45 minutes*
