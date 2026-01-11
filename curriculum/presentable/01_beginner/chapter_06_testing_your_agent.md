# Chapter 6: Testing Your Agent

**Level**: Beginner  
**Duration**: 30-45 minutes  
**Prerequisites**: [Chapter 5 - Memory and Context](./chapter_05_memory_and_context.md)  
**Lab**: All labs (testing practices throughout)

---

## Learning Objectives

By the end of this chapter, you will:

1. **Understand** why testing is critical for agents
2. **Write** unit tests for agent components
3. **Mock** LLM providers for deterministic tests
4. **Implement** integration tests for workflows
5. **Set up** CI/CD for automated testing

---

## 1. Introduction: Why Test Agents?

### The Testing Challenge

**Problem**: Agents are non-deterministic (LLMs give different answers each time).

**Without Tests**:
- Change breaks agent → discover in production → users suffer
- Can't confidently add features
- No way to verify behavior

**With Tests**:
- Catch bugs before deployment
- Safely refactor code
- Document expected behavior
- Enable CI/CD automation

---

## 2. Types of Tests

### Unit Tests
**What**: Test individual components in isolation  
**Example**: Test calculator tool, memory module, retriever  
**Fast**: Yes (no LLM calls)

```python
def test_calculator_add():
    calc = CalculatorTool()
    result = calc.add(2, 3)
    assert result == 5  # Pass!
```

### Integration Tests
**What**: Test components working together  
**Example**: Test agent + tool + memory workflow  
**Fast**: Medium (may use MockProvider)

```python
def test_agent_with_tools():
    agent = AgentOrchestrator(
        llm_provider=MockProvider(),
        tools=[CalculatorTool()]
    )
    response = agent.run("What's 2+2?")
    assert "4" in response
```

### End-to-End Tests
**What**: Test full system with real LLM  
**Example**: User query → agent → tools → response  
**Fast**: No (real API calls)

```python
def test_real_agent_workflow():
    agent = AgentOrchestrator(
        llm_provider=OpenAIProvider(api_key="..."),
        tools=[WeatherTool(), CalendarTool()]
    )
    response = agent.run("Book me a flight to Paris next Friday")
    assert "booking confirmed" in response.lower()
```

---

## 3. Writing Your First Test

### Step 1: Install pytest

```bash
pip install pytest pytest-asyncio
```

### Step 2: Create Test File

Create `labs/00/tests/test_my_agent.py`:

```python
"""
Unit tests for agent components
"""
import pytest
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider
from agent_labs.memory import ConversationMemory

def test_agent_initialization():
    """Test agent can be created"""
    provider = MockProvider()
    agent = AgentOrchestrator(llm_provider=provider)
    assert agent is not None
    assert agent.llm_provider == provider

def test_agent_responds():
    """Test agent generates responses"""
    provider = MockProvider()
    agent = AgentOrchestrator(llm_provider=provider)
    response = agent.run("Hello")
    assert response is not None
    assert len(response) > 0

def test_agent_with_memory():
    """Test agent remembers conversation"""
    provider = MockProvider()
    memory = ConversationMemory(max_turns=5)
    agent = AgentOrchestrator(llm_provider=provider, memory=memory)
    
    agent.run("My name is Sarah")
    agent.run("What's my name?")
    
    history = memory.get_history()
    assert len(history) == 4  # 2 user + 2 agent messages
    assert "Sarah" in history[0]["content"]
```

### Step 3: Run Tests

```bash
pytest labs/00/tests/test_my_agent.py -v
```

**Expected output**:
```
test_agent_initialization PASSED
test_agent_responds PASSED
test_agent_with_memory PASSED
==================== 3 passed in 0.25s ====================
```

✅ All green! Your agent is tested.

---

## 4. Mocking LLM Providers

### Why Mock?

**Problem**: Real LLM calls are:
- Slow (seconds per request)
- Expensive (costs money)
- Non-deterministic (different answers each time)
- Rate-limited (can't run 1000 tests/minute)

**Solution**: Use MockProvider for tests.

### MockProvider Implementation

```python
class MockProvider:
    """Fake LLM that returns predictable responses"""
    
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_count = 0
    
    def generate(self, prompt: str) -> str:
        self.call_count += 1
        
        # Return predefined response if available
        if prompt in self.responses:
            return self.responses[prompt]
        
        # Default: echo prompt
        return f"[Mock] {prompt}"
```

### Using MockProvider in Tests

```python
def test_calculator_tool_usage():
    # Set up mock with expected behavior
    mock = MockProvider(responses={
        "Calculate 5 + 3": "The answer is 8"
    })
    
    agent = AgentOrchestrator(
        llm_provider=mock,
        tools=[CalculatorTool()]
    )
    
    response = agent.run("Calculate 5 + 3")
    
    assert "8" in response
    assert mock.call_count == 1  # Verify LLM was called once
```

---

## 5. Testing Tools

### Test Tool Contracts

```python
def test_calculator_tool_contract():
    """Verify tool has required attributes"""
    calc = CalculatorTool()
    
    # Check contract
    assert hasattr(calc, 'name')
    assert hasattr(calc, 'description')
    assert hasattr(calc, 'execute')
    
    # Check types
    assert isinstance(calc.name, str)
    assert isinstance(calc.description, str)
    assert callable(calc.execute)
```

### Test Tool Behavior

```python
def test_calculator_operations():
    """Test all calculator operations"""
    calc = CalculatorTool()
    
    # Test add
    assert calc.execute("add", 2, 3) == 5
    
    # Test subtract
    assert calc.execute("subtract", 10, 4) == 6
    
    # Test multiply
    assert calc.execute("multiply", 3, 7) == 21
    
    # Test divide
    assert calc.execute("divide", 15, 3) == 5
    
    # Test divide by zero
    result = calc.execute("divide", 10, 0)
    assert "Error" in result or "zero" in result.lower()
```

### Test Error Handling

```python
def test_tool_handles_invalid_inputs():
    """Test tool gracefully handles bad inputs"""
    calc = CalculatorTool()
    
    # Invalid operation
    result = calc.execute("explode", 1, 2)
    assert "Error" in result or "Unknown" in result
    
    # Non-numeric inputs
    result = calc.execute("add", "abc", "def")
    assert "Error" in result or "Invalid" in result
```

---

## 6. Testing Memory

### Test Conversation Memory

```python
def test_conversation_memory_stores_turns():
    """Test memory stores and retrieves turns"""
    memory = ConversationMemory(max_turns=5)
    
    memory.add_turn("user", "Hello")
    memory.add_turn("agent", "Hi there!")
    
    history = memory.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
```

### Test Memory Limits

```python
def test_memory_respects_max_turns():
    """Test memory doesn't exceed limit"""
    memory = ConversationMemory(max_turns=3)
    
    # Add 10 turns
    for i in range(10):
        memory.add_turn("user", f"Message {i}")
    
    history = memory.get_history()
    assert len(history) <= 3  # Should keep only last 3
```

### Test Memory Persistence

```python
def test_long_term_memory_persists():
    """Test data survives across instances"""
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    # Create first instance and store data
    memory1 = LongTermMemory(storage_path=temp_file.name)
    memory1.store("key", "value")
    del memory1  # Destroy instance
    
    # Create second instance and retrieve
    memory2 = LongTermMemory(storage_path=temp_file.name)
    value = memory2.retrieve("key")
    assert value == "value"  # Data persisted!
```

---

## 7. Integration Testing

### Test Full Workflows

```python
def test_rag_agent_workflow():
    """Test agent retrieves and generates correctly"""
    # Set up documents
    doc_store = DocumentStore()
    doc_store.add_document({
        "id": "1",
        "content": "Company vacation policy: 15 days annually"
    })
    
    # Set up agent
    retriever = VectorRetriever(doc_store, top_k=1)
    mock = MockProvider(responses={
        "Based on context, answer: How many vacation days?": 
        "Employees get 15 vacation days annually."
    })
    
    agent = AgentOrchestrator(
        llm_provider=mock,
        tools=[retriever]
    )
    
    # Test query
    response = agent.run("How many vacation days?")
    assert "15" in response
    assert "vacation" in response.lower()
```

### Test Multi-Tool Workflows

```python
def test_agent_uses_multiple_tools():
    """Test agent chains tools together"""
    mock = MockProvider()
    calc = CalculatorTool()
    weather = WeatherTool()
    
    agent = AgentOrchestrator(
        llm_provider=mock,
        tools=[calc, weather]
    )
    
    # Agent should be able to use either tool
    calc_response = agent.run("What's 5 + 5?")
    weather_response = agent.run("Weather in Paris?")
    
    assert calc_response is not None
    assert weather_response is not None
```

---

## 8. CI/CD: Automated Testing

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Test Agent

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src/agent_labs
    
    - name: Check coverage
      run: |
        pytest tests/ --cov=src/agent_labs --cov-report=term-missing --cov-fail-under=80
```

**What this does**:
- Runs on every push/PR
- Installs dependencies
- Runs all tests
- Checks code coverage (must be >80%)
- Fails if tests fail (prevents bad merges)

---

## 9. Hands-On Exercises

### Exercise 1: Test a New Tool

Create a weather tool and write 3 tests:

```python
def test_weather_tool_valid_city():
    """Test weather tool with valid city"""
    weather = WeatherTool()
    result = weather.get_weather("Paris")
    assert result is not None
    assert "temp" in result

def test_weather_tool_invalid_city():
    """Test weather tool with unknown city"""
    weather = WeatherTool()
    result = weather.get_weather("NonexistentCity")
    assert "unknown" in result["conditions"].lower()

def test_weather_tool_empty_input():
    """Test weather tool with empty input"""
    weather = WeatherTool()
    result = weather.get_weather("")
    assert "error" in str(result).lower() or result is None
```

### Exercise 2: Test Memory Edge Cases

```python
def test_memory_handles_empty_content():
    memory = ConversationMemory()
    memory.add_turn("user", "")
    history = memory.get_history()
    assert len(history) == 1

def test_memory_handles_very_long_content():
    memory = ConversationMemory()
    long_text = "a" * 10000
    memory.add_turn("user", long_text)
    history = memory.get_history()
    assert len(history[0]["content"]) == 10000
```

### Exercise 3: Measure Test Coverage

```bash
pytest tests/ --cov=src/agent_labs --cov-report=html
open htmlcov/index.html  # View coverage report
```

Aim for >80% coverage on critical modules.

---

## 10. Best Practices

### ✅ Do's
- Test all public functions
- Use MockProvider for unit tests
- Test error cases (not just happy path)
- Run tests before every commit
- Automate tests in CI/CD

### ❌ Don'ts
- Don't test private functions (focus on interfaces)
- Don't use real LLMs in unit tests (expensive/slow)
- Don't skip error case tests
- Don't commit failing tests

---

## 11. Key Concepts Summary

| Concept | What It Is | When to Use |
|---------|------------|-------------|
| **Unit Test** | Test one component in isolation | Every function |
| **Integration Test** | Test components working together | Workflows |
| **MockProvider** | Fake LLM for testing | Unit/integration tests |
| **pytest** | Python testing framework | All tests |
| **Code Coverage** | % of code tested | Measure quality |

---

## 12. Glossary

- **Unit Test**: Tests a single function/component in isolation
- **Integration Test**: Tests multiple components working together
- **End-to-End Test**: Tests full system from user input to output
- **Mock**: Fake object that simulates real component behavior
- **Assertion**: Check that expected == actual (e.g., `assert result == 5`)
- **Code Coverage**: Percentage of code lines executed by tests
- **CI/CD**: Continuous Integration / Continuous Deployment (automated testing)

---

## 13. What's Next?

✅ **You've completed**: Testing agents comprehensively  
🎯 **Next chapter**: [Chapter 7 - Final Project](./chapter_07_final_project.md)  
🔬 **Practice**: Write tests for all your lab exercises

### Skills Unlocked
- ✅ Write unit tests for components
- ✅ Mock LLM providers for deterministic tests
- ✅ Test memory and tools
- ✅ Implement integration tests
- ✅ Set up CI/CD automation

### Preview: Chapter 7 (Final Project)
In the final chapter, you'll:
- Build a complete agent from scratch
- Integrate all concepts (RAG, tools, memory, testing)
- Deploy your agent
- Plan next steps for learning

**The Big Idea**: You've learned all the fundamentals. Now build something real!

---

## 14. Self-Assessment Quiz

1. **Why mock LLM providers in tests?**
   - A) They're faster, cheaper, and deterministic
   - B) Real LLMs don't work in tests
   - C) Mocks are more accurate
   - D) No reason—always use real LLMs

2. **What's a unit test?**
   - A) Test for one specific component
   - B) Test for entire system
   - C) Test that measures time
   - D) Test that uses real LLMs

3. **What does `assert result == 5` do?**
   - A) Sets result to 5
   - B) Checks if result equals 5, fails test if not
   - C) Prints result
   - D) Does nothing

4. **When should you run tests?**
   - A) Only before deployment
   - B) Before every commit (via CI/CD)
   - C) Once a month
   - D) Never—tests are optional

5. **What's code coverage?**
   - A) Number of tests
   - B) Percentage of code executed by tests
   - C) Test execution time
   - D) Number of bugs found

6. **Why test error cases?**
   - A) To make tests longer
   - B) To ensure agent handles failures gracefully
   - C) Error tests are not necessary
   - D) Only test happy paths

7. **What's an integration test?**
   - A) Tests one function only
   - B) Tests multiple components working together
   - C) Tests deployment process
   - D) Tests user interface

8. **What's a good code coverage target?**
   - A) 10-20%
   - B) 80-90%
   - C) 100% (every line)
   - D) Coverage doesn't matter

9. **What tool do we use for Python testing?**
   - A) unittest
   - B) pytest
   - C) jest
   - D) mocha

10. **When should you use real LLMs in tests?**
    - A) Always
    - B) Only in end-to-end tests (sparingly)
    - C) Never
    - D) Only on Fridays

### Answers
1. A, 2. A, 3. B, 4. B, 5. B, 6. B, 7. B, 8. B, 9. B, 10. B

---

## Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://realpython.com/pytest-python-testing/)
- [GitHub Actions CI/CD](https://docs.github.com/en/actions)

---

**Chapter Complete!** 🎉  
You've learned how to test agents thoroughly!

**Next**: [Chapter 7 - Final Project →](./chapter_07_final_project.md)

---

*Estimated reading time: 25 minutes*  
*Hands-on exercises: 20 minutes*  
*Total chapter time: 45 minutes*
