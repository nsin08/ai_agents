# Tools Framework

A production-grade tool execution system for AI agents with contract-based validation, built-in tools, and comprehensive error handling.

## Overview

The tools framework provides:
- **Contract-based validation**: Define schemas for inputs/outputs
- **Execution status taxonomy**: 5 distinct status types for precise error tracking
- **Built-in tools**: Calculator, WebSearch, FileRead with security
- **Pre-execution validation**: Pydantic and JSON schema support
- **Rich result metadata**: Latency, retries, timestamps, custom metadata

## Architecture

```
tools/
├── contract.py      # ToolContract, ToolResult, ExecutionStatus
├── validators.py    # Pydantic and JSON schema validation
├── registry.py      # ToolRegistry with validation
├── builtin.py       # Calculator, WebSearch, FileRead
└── base.py          # Tool ABC, MockTool
```

## Quick Start

### Basic Tool Usage

```python
from agent_labs.tools import Calculator, ToolRegistry

# Create and register tool
registry = ToolRegistry()
calc = Calculator()
registry.register(calc)

# Execute with automatic validation
result = await registry.execute("calculator", operation="add", a=5, b=3)

if result.success:
    print(f"Result: {result.output}")  # Result: 8.0
    print(f"Latency: {result.latency_ms}ms")
else:
    print(f"Error: {result.error}")
```

### Creating Custom Tools

```python
from agent_labs.tools import Tool, ToolContract, ToolResult, ExecutionStatus
from pydantic import BaseModel, Field

class GreetingInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    language: str = Field(default="en", pattern="^(en|es|fr)$")

class GreetingTool(Tool):
    def __init__(self):
        self.contract = ToolContract(
            name="greeting",
            description="Generate greetings in multiple languages",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "language": {"type": "string", "enum": ["en", "es", "fr"]}
                },
                "required": ["name"]
            },
            output_schema={"type": "string"},
            version="1.0.0",
            tags=["social", "multilingual"]
        )
    
    @property
    def name(self) -> str:
        return "greeting"
    
    @property
    def description(self) -> str:
        return "Generate greetings"
    
    async def execute(self, **kwargs) -> ToolResult:
        import time
        start = time.perf_counter()
        
        # Validate inputs
        from agent_labs.tools.validators import ToolInputValidator
        is_valid, data, error = ToolInputValidator.validate_with_pydantic(
            kwargs, GreetingInput
        )
        
        if not is_valid:
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                output=None,
                error=f"Invalid input: {error}",
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        # Execute tool logic
        greetings = {
            "en": f"Hello, {data['name']}!",
            "es": f"¡Hola, {data['name']}!",
            "fr": f"Bonjour, {data['name']}!"
        }
        
        output = greetings.get(data.get("language", "en"))
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=output,
            metadata={
                "tool_name": self.name,
                "language": data.get("language", "en"),
                "timestamp": time.time()
            },
            latency_ms=latency_ms
        )
    
    def get_schema(self) -> dict:
        return self.contract.to_dict()
```

## Core Concepts

### ToolContract

Defines the interface for a tool:

```python
from agent_labs.tools import ToolContract

contract = ToolContract(
    name="my_tool",
    description="What the tool does",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "number"}
        },
        "required": ["param1"]
    },
    output_schema={"type": "string"},
    version="1.0.0",
    tags=["category", "feature"],
    constraints={
        "max_execution_time_ms": 5000,
        "allowed_environments": ["production", "staging"]
    }
)

# Serialize to dict
schema = contract.to_dict()
```

### ExecutionStatus

5-level status taxonomy for precise error tracking:

```python
from agent_labs.tools import ExecutionStatus

# Success
ExecutionStatus.SUCCESS        # Tool executed successfully

# Failures
ExecutionStatus.FAILURE        # Generic execution failure
ExecutionStatus.TIMEOUT        # Exceeded time limits
ExecutionStatus.INVALID_INPUT  # Input validation failed
ExecutionStatus.NOT_FOUND      # Tool or resource not found
```

### ToolResult

Rich execution results with metadata:

```python
from agent_labs.tools import ToolResult, ExecutionStatus

result = ToolResult(
    status=ExecutionStatus.SUCCESS,
    output={"data": "result"},
    error=None,
    metadata={
        "tool_name": "calculator",
        "operation": "add",
        "cache_hit": True
    },
    latency_ms=15,
    retries=0,
    timestamp=1699564800.0
)

# Properties
if result.success:  # Computed from status
    print(result.output)

if result.failed:   # Checks if status is error
    print(result.error)

# Serialization
data = result.to_dict()
```

## Built-in Tools

### Calculator

Arithmetic operations with validation:

```python
from agent_labs.tools import Calculator, ToolRegistry

calc = Calculator()
registry = ToolRegistry()
registry.register(calc)

# Addition
result = await registry.execute("calculator", operation="add", a=10, b=5)
# Output: 15.0

# Division (with error handling)
result = await registry.execute("calculator", operation="divide", a=10, b=0)
# Status: FAILURE
# Error: "Division by zero"

# Invalid operation
result = await registry.execute("calculator", operation="power", a=2, b=3)
# Status: INVALID_INPUT
# Error: "operation: Input should be 'add', 'subtract', 'multiply' or 'divide'"
```

**Supported Operations:**
- `add`: Addition
- `subtract`: Subtraction
- `multiply`: Multiplication
- `divide`: Division (with zero check)

**Input Schema:**
```python
{
    "operation": str,  # "add" | "subtract" | "multiply" | "divide"
    "a": float,        # First operand
    "b": float         # Second operand
}
```

### WebSearch

Mock web search (no real HTTP):

```python
from agent_labs.tools import WebSearch, ToolRegistry

search = WebSearch()
registry = ToolRegistry()
registry.register(search)

result = await registry.execute(
    "web_search",
    query="Python asyncio tutorial",
    max_results=5,
    language="en"
)

# Output: List[Dict]
# [
#     {
#         "title": "Result 1",
#         "url": "https://example.com/1",
#         "snippet": "Python asyncio tutorial content...",
#         "rank": 1
#     },
#     ...
# ]
```

**Input Schema:**
```python
{
    "query": str,         # 1-500 characters
    "max_results": int,   # 1-100, default 10
    "language": str       # Optional, e.g., "en", "es"
}
```

**Metadata:**
- `is_mock`: Always `True` (no real HTTP)
- `language`: Query language
- `result_count`: Number of results returned

### FileRead

Sandboxed file reading with security:

```python
from agent_labs.tools import FileRead, ToolRegistry
import tempfile

# Create with allowed roots (sandbox)
file_read = FileRead(
    allowed_roots=[
        "/home/user/data",
        "/tmp"
    ],
    max_file_size=1024 * 1024  # 1MB default
)

registry = ToolRegistry()
registry.register(file_read)

# Read text file
result = await registry.execute(
    "file_read",
    path="/home/user/data/config.json"
)
# Output: File contents as string

# Read binary file (auto-detects and base64 encodes)
result = await registry.execute(
    "file_read",
    path="/home/user/data/image.png"
)
# Output: Base64-encoded string
# Metadata: {"is_binary": True}

# Security violation (path outside allowed roots)
result = await registry.execute(
    "file_read",
    path="/etc/passwd"
)
# Status: FAILURE
# Error: "Access denied: Path outside allowed roots"
# Metadata: {"security_violation": True}
```

**Input Schema:**
```python
{
    "path": str,              # Absolute or relative path
    "encoding": str,          # Default "utf-8"
    "max_size_bytes": int     # Optional, override default
}
```

**Security Features:**
- **Sandboxed access**: Only reads from `allowed_roots`
- **Path traversal prevention**: Resolves paths and validates
- **File size limits**: Configurable max size (default 1MB, max 10MB)
- **Binary handling**: Auto-detects and base64 encodes

**Metadata:**
- `file_size_bytes`: Size of file read
- `is_binary`: Whether file was binary
- `security_violation`: If access was denied

**Contract Constraints:**
```python
{
    "allowed_roots": ["/home/user/data", "/tmp"],
    "max_file_size": 1048576
}
```

## Input Validation

### Pydantic Validation (Recommended)

```python
from pydantic import BaseModel, Field
from agent_labs.tools.validators import ToolInputValidator

class MyInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# Validate
inputs = {"name": "Alice", "age": 30, "email": "alice@example.com"}
is_valid, data, error = ToolInputValidator.validate_with_pydantic(
    inputs, MyInput
)

if is_valid:
    print(data)  # {"name": "Alice", "age": 30, "email": "alice@example.com"}
else:
    print(error)
```

**Benefits:**
- Type coercion (string "30" → int 30)
- Rich validation (min/max, patterns, custom validators)
- Clear error messages
- IDE autocomplete with Pydantic models

### JSON Schema Validation

```python
from agent_labs.tools.validators import ToolInputValidator

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

inputs = {"name": "Bob", "age": 25}
is_valid, data, error = ToolInputValidator.validate_with_json_schema(
    inputs, schema
)
```

**Use Cases:**
- When you have existing JSON schemas
- When you don't want Pydantic dependency
- When schema is dynamically generated

## ToolRegistry

Central registry for tool management with validation:

```python
from agent_labs.tools import ToolRegistry, Calculator, WebSearch

registry = ToolRegistry()

# Register tools
calc = Calculator()
search = WebSearch()
registry.register(calc)
registry.register(search)

# List registered tools
tools = registry.list_tools()  # ["calculator", "web_search"]

# Get tool instance
tool = registry.get("calculator")

# Execute with validation (default)
result = await registry.execute("calculator", operation="add", a=5, b=3)

# Execute without validation (skip input checks)
result = await registry.execute(
    "calculator",
    validate_input=False,  # Skip validation
    operation="add",
    a=5,
    b=3
)

# Batch execution (sequential)
operations = [
    ("calculator", {"operation": "add", "a": 5, "b": 3}),
    ("calculator", {"operation": "multiply", "a": 2, "b": 4}),
    ("web_search", {"query": "Python", "max_results": 5})
]
results = await registry.execute_batch(operations)
# Returns: List[ToolResult]

# Get all tool schemas (for tool discovery)
schemas = registry.get_all_schemas()
# {
#     "calculator": {...schema...},
#     "web_search": {...schema...}
# }

# Unregister tool
removed = registry.unregister("calculator")  # True

# Clear all tools
registry.clear()

# Check operations
if "calculator" in registry:
    print(f"Registry has {len(registry)} tools")
```

## Error Handling

### Best Practices

```python
from agent_labs.tools import ExecutionStatus

result = await registry.execute("my_tool", **params)

# Pattern 1: Check status directly
if result.status == ExecutionStatus.SUCCESS:
    process(result.output)
elif result.status == ExecutionStatus.INVALID_INPUT:
    log_validation_error(result.error)
elif result.status == ExecutionStatus.TIMEOUT:
    retry_with_longer_timeout()
else:
    handle_generic_error(result.error)

# Pattern 2: Use success/failed properties
if result.success:
    return result.output
else:
    raise ToolExecutionError(result.error)

# Pattern 3: Check specific failures
if result.failed:
    if result.status == ExecutionStatus.NOT_FOUND:
        # Tool or resource not found
        pass
    elif result.status == ExecutionStatus.TIMEOUT:
        # Timeout occurred
        pass
```

### Exception Handling in Tools

```python
import time
from agent_labs.tools import Tool, ToolResult, ExecutionStatus

class RiskyTool(Tool):
    async def execute(self, **kwargs) -> ToolResult:
        start = time.perf_counter()
        
        try:
            # Risky operation
            output = await self._do_risky_operation(kwargs)
            
            return ToolResult(
                status=ExecutionStatus.SUCCESS,
                output=output,
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except ValueError as e:
            # Known validation error
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                output=None,
                error=f"Invalid input: {e}",
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except TimeoutError:
            return ToolResult(
                status=ExecutionStatus.TIMEOUT,
                output=None,
                error="Operation timed out",
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
        
        except Exception as e:
            # Unexpected error
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                output=None,
                error=f"Unexpected error: {e}",
                metadata={"exception_type": type(e).__name__},
                latency_ms=int((time.perf_counter() - start) * 1000)
            )
```

## Security Considerations

### FileRead Sandbox

Always use `allowed_roots` to restrict file access:

```python
from agent_labs.tools import FileRead

# INSECURE: No restrictions
file_read = FileRead()  # Can read ANY file!

# SECURE: Restricted to specific directories
file_read = FileRead(allowed_roots=[
    "/home/user/data",
    "/tmp/uploads"
])
```

### Input Validation

Always validate inputs before execution:

```python
# ToolRegistry validates by default
result = await registry.execute("my_tool", **params)  # Validates

# Manual validation in custom tools
from agent_labs.tools.validators import ToolInputValidator

is_valid, data, error = ToolInputValidator.validate_with_pydantic(
    inputs, MyInputModel
)

if not is_valid:
    return ToolResult(
        status=ExecutionStatus.INVALID_INPUT,
        output=None,
        error=error
    )
```

### Path Traversal Prevention

FileRead automatically prevents path traversal:

```python
file_read = FileRead(allowed_roots=["/home/user/data"])

# These are blocked:
# path="../../../etc/passwd"
# path="/home/user/data/../../../etc/passwd"
# path="../../secrets.txt"

# All paths are resolved and validated before access
```

## Performance Tracking

All ToolResult objects include performance metrics:

```python
result = await registry.execute("my_tool", **params)

print(f"Execution time: {result.latency_ms}ms")
print(f"Retry attempts: {result.retries}")
print(f"Timestamp: {result.timestamp}")

# Aggregate metrics across multiple executions
results = await registry.execute_batch(operations)
total_latency = sum(r.latency_ms for r in results)
avg_latency = total_latency / len(results)
failed_count = sum(1 for r in results if r.failed)
```

## Testing

### Unit Testing Tools

```python
import pytest
from agent_labs.tools import Calculator, ExecutionStatus

@pytest.mark.asyncio
async def test_calculator_addition():
    calc = Calculator()
    result = await calc.execute(operation="add", a=5, b=3)
    
    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == 8.0
    assert result.success
    assert not result.failed
    assert result.latency_ms >= 0
    assert "tool_name" in result.metadata

@pytest.mark.asyncio
async def test_calculator_division_by_zero():
    calc = Calculator()
    result = await calc.execute(operation="divide", a=10, b=0)
    
    assert result.status == ExecutionStatus.FAILURE
    assert result.failed
    assert "division by zero" in result.error.lower()
```

### Integration Testing with Registry

```python
import pytest
from agent_labs.tools import ToolRegistry, Calculator, WebSearch

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(Calculator())
    reg.register(WebSearch())
    return reg

@pytest.mark.asyncio
async def test_batch_execution(registry):
    operations = [
        ("calculator", {"operation": "add", "a": 5, "b": 3}),
        ("web_search", {"query": "Python", "max_results": 5})
    ]
    
    results = await registry.execute_batch(operations)
    
    assert len(results) == 2
    assert all(r.success for r in results)
```

## Migration from v1 (Old API)

If upgrading from the old boolean-based API:

```python
# OLD API (v1)
result = ToolResult(
    success=True,
    output="data",
    error=None
)
if result.success:
    process(result.output)

# NEW API (v2)
from agent_labs.tools import ExecutionStatus

result = ToolResult(
    status=ExecutionStatus.SUCCESS,
    output="data",
    metadata={"tool_name": "my_tool"}
)
if result.success:  # Property still works!
    process(result.output)
```

**Key Changes:**
- ✅ `success` boolean → `status` enum (more precise)
- ✅ `success` property still available (computed from status)
- ✅ Added `metadata`, `latency_ms`, `retries`, `timestamp`
- ✅ Added `to_dict()` method for serialization
- ✅ ToolRegistry moved from `base.py` to `registry.py`
- ✅ Added `validators.py` module

## API Reference

### Classes

- **`Tool`**: Abstract base class for all tools
- **`ToolContract`**: Contract defining tool interface
- **`ToolResult`**: Rich execution result with metadata
- **`ExecutionStatus`**: Enum for execution outcomes
- **`ToolRegistry`**: Central tool management with validation
- **`ToolInputValidator`**: Input validation utilities
- **`ToolOutputValidator`**: Output validation utilities

### Built-in Tools

- **`Calculator`**: Arithmetic operations
- **`WebSearch`**: Mock web search
- **`FileRead`**: Sandboxed file reading

### Pydantic Models

- **`CalculatorInput`**: Calculator input schema
- **`WebSearchInput`**: Web search input schema
- **`FileReadInput`**: File read input schema

## Contributing

When adding new built-in tools:

1. Create tool class inheriting from `Tool`
2. Define `ToolContract` with schemas
3. Implement `execute()` with validation
4. Track `latency_ms` and include `metadata`
5. Use `ExecutionStatus` enum for all results
6. Add Pydantic model to `validators.py`
7. Export from `__init__.py`
8. Add comprehensive tests

Example structure:
```python
class MyTool(Tool):
    def __init__(self):
        self.contract = ToolContract(...)
    
    @property
    def name(self) -> str: ...
    
    @property
    def description(self) -> str: ...
    
    async def execute(self, **kwargs) -> ToolResult:
        start = time.perf_counter()
        # Validate, execute, handle errors
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=output,
            metadata={"tool_name": self.name},
            latency_ms=int((time.perf_counter() - start) * 1000)
        )
    
    def get_schema(self) -> dict:
        return self.contract.to_dict()
```

## License

See project root LICENSE file.
