"""
Comprehensive tests for tool contracts, validation, and built-in tools.

Tests:
1. ToolContract creation and validation
2. ExecutionStatus enum
3. ToolResult enhanced fields (metadata, latency, retries)
4. Input validation (Pydantic and JSON schema)
5. Built-in tools: Calculator, WebSearch, FileRead
6. Error scenarios and edge cases
"""

import pytest
import tempfile
from pathlib import Path
from src.agent_labs.tools import (
    Tool,
    ToolResult,
    ExecutionStatus,
    ToolContract,
    ToolRegistry,
    ToolInputValidator,
    Calculator,
    WebSearch,
    FileRead,
    CalculatorInput,
)


class TestToolContract:
    """Tests for ToolContract dataclass."""

    def test_tool_contract_creation(self):
        """Test creating a ToolContract."""
        contract = ToolContract(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {}, "required": []},
        )
        
        assert contract.name == "test_tool"
        assert contract.description == "A test tool"
        assert contract.version == "1.0.0"  # default
        assert contract.tags == []  # default
    
    def test_tool_contract_with_tags(self):
        """Test ToolContract with tags."""
        contract = ToolContract(
            name="calculator",
            description="Math operations",
            input_schema={},
            tags=["math", "arithmetic"],
        )
        
        assert "math" in contract.tags
        assert "arithmetic" in contract.tags
    
    def test_tool_contract_to_dict(self):
        """Test converting contract to dictionary."""
        contract = ToolContract(
            name="test_tool",
            description="Test",
            input_schema={"type": "object"},
            version="2.0.0",
        )
        
        contract_dict = contract.to_dict()
        assert isinstance(contract_dict, dict)
        assert contract_dict["name"] == "test_tool"
        assert contract_dict["version"] == "2.0.0"


class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""

    def test_execution_status_values(self):
        """Test ExecutionStatus has all required values."""
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.FAILURE.value == "failure"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.INVALID_INPUT.value == "invalid_input"
        assert ExecutionStatus.NOT_FOUND.value == "not_found"


class TestEnhancedToolResult:
    """Tests for enhanced ToolResult with metadata and timing."""

    def test_tool_result_with_metadata(self):
        """Test ToolResult with metadata field."""
        result = ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=42,
            metadata={"tool_name": "calculator", "operation": "add"},
        )
        
        assert result.metadata["tool_name"] == "calculator"
        assert result.metadata["operation"] == "add"
    
    def test_tool_result_with_latency(self):
        """Test ToolResult with latency tracking."""
        result = ToolResult(
            status=ExecutionStatus.SUCCESS,
            output="result",
            latency_ms=15.3,
        )
        
        assert result.latency_ms == 15.3
    
    def test_tool_result_with_retries(self):
        """Test ToolResult with retry count."""
        result = ToolResult(
            status=ExecutionStatus.SUCCESS,
            output="result",
            retries=2,
        )
        
        assert result.retries == 2
    
    def test_tool_result_success_property(self):
        """Test ToolResult.success property."""
        success_result = ToolResult(status=ExecutionStatus.SUCCESS)
        failure_result = ToolResult(status=ExecutionStatus.FAILURE)
        
        assert success_result.success is True
        assert failure_result.success is False
    
    def test_tool_result_failed_property(self):
        """Test ToolResult.failed property."""
        success_result = ToolResult(status=ExecutionStatus.SUCCESS)
        failure_result = ToolResult(status=ExecutionStatus.FAILURE)
        timeout_result = ToolResult(status=ExecutionStatus.TIMEOUT)
        
        assert success_result.failed is False
        assert failure_result.failed is True
        assert timeout_result.failed is True
    
    def test_tool_result_to_dict(self):
        """Test converting ToolResult to dictionary."""
        result = ToolResult(
            status=ExecutionStatus.SUCCESS,
            output=42,
            metadata={"test": "data"},
            latency_ms=10.5,
        )
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["status"] == "success"
        assert result_dict["output"] == 42
        assert result_dict["success"] is True


class TestInputValidation:
    """Tests for input validation with Pydantic."""

    def test_validate_with_pydantic_success(self):
        """Test successful validation with Pydantic."""
        inputs = {"operation": "add", "a": 5, "b": 3}
        
        is_valid, data, error = ToolInputValidator.validate_with_pydantic(
            inputs, CalculatorInput
        )
        
        assert is_valid is True
        assert data["operation"] == "add"
        assert data["a"] == 5.0  # coerced to float
        assert error is None
    
    def test_validate_with_pydantic_missing_field(self):
        """Test validation failure with missing required field."""
        inputs = {"operation": "add", "a": 5}  # missing 'b'
        
        is_valid, data, error = ToolInputValidator.validate_with_pydantic(
            inputs, CalculatorInput
        )
        
        assert is_valid is False
        assert data is None
        assert "b" in error.lower()
    
    def test_validate_with_pydantic_invalid_type(self):
        """Test validation failure with invalid type."""
        inputs = {"operation": "add", "a": "not a number", "b": 3}
        
        is_valid, data, error = ToolInputValidator.validate_with_pydantic(
            inputs, CalculatorInput
        )
        
        assert is_valid is False
        assert data is None
        assert error is not None
    
    def test_validate_with_json_schema_success(self):
        """Test JSON schema validation success."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
            "required": ["name"],
        }
        inputs = {"name": "Alice", "age": 30}
        
        is_valid, data, error = ToolInputValidator.validate_with_json_schema(
            inputs, schema
        )
        
        assert is_valid is True
        assert data == inputs
        assert error is None
    
    def test_validate_with_json_schema_missing_required(self):
        """Test JSON schema validation failure with missing field."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        inputs = {}  # missing 'name'
        
        is_valid, data, error = ToolInputValidator.validate_with_json_schema(
            inputs, schema
        )
        
        assert is_valid is False
        assert "name" in error


class TestCalculatorTool:
    """Tests for Calculator built-in tool."""

    @pytest.mark.asyncio
    async def test_calculator_addition(self):
        """Test calculator addition operation."""
        calc = Calculator()
        result = await calc.execute(operation="add", a=5, b=3)
        
        assert result.success is True
        assert result.output == 8.0
        assert result.status == ExecutionStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_calculator_subtraction(self):
        """Test calculator subtraction operation."""
        calc = Calculator()
        result = await calc.execute(operation="subtract", a=10, b=3)
        
        assert result.success is True
        assert result.output == 7.0
    
    @pytest.mark.asyncio
    async def test_calculator_multiplication(self):
        """Test calculator multiplication operation."""
        calc = Calculator()
        result = await calc.execute(operation="multiply", a=4, b=5)
        
        assert result.success is True
        assert result.output == 20.0
    
    @pytest.mark.asyncio
    async def test_calculator_division(self):
        """Test calculator division operation."""
        calc = Calculator()
        result = await calc.execute(operation="divide", a=15, b=3)
        
        assert result.success is True
        assert result.output == 5.0
    
    @pytest.mark.asyncio
    async def test_calculator_division_by_zero(self):
        """Test calculator handles division by zero."""
        calc = Calculator()
        result = await calc.execute(operation="divide", a=10, b=0)
        
        assert result.success is False
        assert result.status == ExecutionStatus.FAILURE
        assert "zero" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_calculator_invalid_operation(self):
        """Test calculator rejects invalid operation."""
        calc = Calculator()
        result = await calc.execute(operation="invalid", a=5, b=3)
        
        assert result.success is False
        assert result.status == ExecutionStatus.INVALID_INPUT
    
    @pytest.mark.asyncio
    async def test_calculator_missing_parameter(self):
        """Test calculator validates required parameters."""
        calc = Calculator()
        result = await calc.execute(operation="add", a=5)  # missing 'b'
        
        assert result.success is False
        assert result.status == ExecutionStatus.INVALID_INPUT
    
    @pytest.mark.asyncio
    async def test_calculator_tracks_latency(self):
        """Test calculator tracks execution time."""
        calc = Calculator()
        result = await calc.execute(operation="add", a=1, b=2)
        
        assert result.latency_ms >= 0
    
    @pytest.mark.asyncio
    async def test_calculator_includes_metadata(self):
        """Test calculator includes metadata in result."""
        calc = Calculator()
        result = await calc.execute(operation="multiply", a=3, b=4)
        
        assert "tool_name" in result.metadata
        assert result.metadata["tool_name"] == "calculator"
        assert result.metadata["operation"] == "multiply"
    
    def test_calculator_get_schema(self):
        """Test calculator returns valid schema."""
        calc = Calculator()
        schema = calc.get_schema()
        
        assert schema["name"] == "calculator"
        assert "input_schema" in schema
        assert "add" in str(schema)


class TestWebSearchTool:
    """Tests for WebSearch built-in tool."""

    @pytest.mark.asyncio
    async def test_web_search_basic(self):
        """Test web search basic execution."""
        search = WebSearch()
        result = await search.execute(query="python tutorial")
        
        assert result.success is True
        assert result.status == ExecutionStatus.SUCCESS
        assert "results" in result.output
    
    @pytest.mark.asyncio
    async def test_web_search_returns_results(self):
        """Test web search returns list of results."""
        search = WebSearch()
        result = await search.execute(query="test query", max_results=5)
        
        assert len(result.output["results"]) == 5
        for item in result.output["results"]:
            assert "title" in item
            assert "url" in item
            assert "snippet" in item
    
    @pytest.mark.asyncio
    async def test_web_search_respects_max_results(self):
        """Test web search respects max_results parameter."""
        search = WebSearch()
        result = await search.execute(query="test", max_results=3)
        
        assert len(result.output["results"]) == 3
    
    @pytest.mark.asyncio
    async def test_web_search_empty_query_fails(self):
        """Test web search rejects empty query."""
        search = WebSearch()
        result = await search.execute(query="")
        
        assert result.success is False
        assert result.status == ExecutionStatus.INVALID_INPUT
    
    @pytest.mark.asyncio
    async def test_web_search_includes_metadata(self):
        """Test web search includes metadata."""
        search = WebSearch()
        result = await search.execute(query="test")
        
        assert result.metadata["is_mock"] is True
        assert "tool_name" in result.metadata


class TestFileReadTool:
    """Tests for FileRead built-in tool."""

    @pytest.mark.asyncio
    async def test_file_read_basic(self):
        """Test file read basic execution."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            file_read = FileRead(allowed_roots=[tempfile.gettempdir()])
            result = await file_read.execute(path=temp_path)
            
            assert result.success is True
            assert result.output["content"] == "Test content"
            assert result.output["is_binary"] is False
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_file_read_nonexistent_file(self):
        """Test file read handles nonexistent file."""
        # Use a path within allowed roots but that doesn't exist
        nonexistent_path = Path(tempfile.gettempdir()) / "nonexistent_file_test.txt"
        
        file_read = FileRead(allowed_roots=[tempfile.gettempdir()])
        result = await file_read.execute(path=str(nonexistent_path))
        
        assert result.success is False
        assert result.status == ExecutionStatus.FAILURE
        assert "not found" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_file_read_sandbox_violation(self):
        """Test file read enforces sandbox security."""
        file_read = FileRead(allowed_roots=[tempfile.gettempdir()])
        
        # Try to read outside allowed roots
        result = await file_read.execute(path="/etc/passwd")
        
        assert result.success is False
        assert result.status == ExecutionStatus.FAILURE
        assert "denied" in result.error.lower() or "outside" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_file_read_tracks_file_size(self):
        """Test file read includes file size in output."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test")
            temp_path = f.name
        
        try:
            file_read = FileRead(allowed_roots=[tempfile.gettempdir()])
            result = await file_read.execute(path=temp_path)
            
            assert "size_bytes" in result.output
            assert result.output["size_bytes"] == 4  # "Test" is 4 bytes
        finally:
            Path(temp_path).unlink()
    
    def test_file_read_get_schema_includes_constraints(self):
        """Test file read schema includes security constraints."""
        file_read = FileRead(allowed_roots=["/tmp", "/var/tmp"])
        schema = file_read.get_schema()
        
        assert "constraints" in schema
        assert "allowed_roots" in schema["constraints"]


class TestToolRegistryWithValidation:
    """Tests for ToolRegistry with input validation."""

    @pytest.mark.asyncio
    async def test_registry_validates_inputs_by_default(self):
        """Test registry validates inputs by default."""
        registry = ToolRegistry()
        calc = Calculator()
        registry.register(calc)
        
        # Valid inputs
        result = await registry.execute("calculator", operation="add", a=5, b=3)
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_registry_rejects_invalid_inputs(self):
        """Test registry rejects invalid inputs."""
        registry = ToolRegistry()
        calc = Calculator()
        registry.register(calc)
        
        # Missing required field
        result = await registry.execute("calculator", operation="add", a=5)
        assert result.success is False
        assert result.status == ExecutionStatus.INVALID_INPUT
    
    @pytest.mark.asyncio
    async def test_registry_can_skip_validation(self):
        """Test registry can skip validation if requested."""
        registry = ToolRegistry()
        calc = Calculator()
        registry.register(calc)
        
        # Execute without validation (tool will validate internally)
        result = await registry.execute(
            "calculator",
            validate_input=False,
            operation="add",
            a=5,
            b=3
        )
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_registry_execute_batch(self):
        """Test registry batch execution."""
        registry = ToolRegistry()
        calc = Calculator()
        registry.register(calc)
        
        operations = [
            {"tool": "calculator", "params": {"operation": "add", "a": 5, "b": 3}},
            {"tool": "calculator", "params": {"operation": "multiply", "a": 2, "b": 4}},
        ]
        
        results = await registry.execute_batch(operations)
        
        assert len(results) == 2
        assert results[0].output == 8.0
        assert results[1].output == 8.0
    
    def test_registry_get_all_schemas(self):
        """Test registry returns all tool schemas."""
        registry = ToolRegistry()
        calc = Calculator()
        search = WebSearch()
        
        registry.register(calc)
        registry.register(search)
        
        schemas = registry.get_all_schemas()
        
        assert len(schemas) == 2
        assert "calculator" in schemas
        assert "web_search" in schemas


class TestErrorScenarios:
    """Tests for error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_tool_execution_exception_handling(self):
        """Test registry handles tool exceptions gracefully."""
        class BrokenTool(Tool):
            def __init__(self):
                self.name = "broken"
            
            async def execute(self, **kwargs):
                raise ValueError("Intentional error")
            
            def get_schema(self):
                return {"name": "broken"}
        
        registry = ToolRegistry()
        registry.register(BrokenTool())
        
        result = await registry.execute("broken")
        
        assert result.success is False
        assert result.status == ExecutionStatus.FAILURE
        assert "error" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_tool_not_found_error(self):
        """Test registry handles missing tool gracefully."""
        registry = ToolRegistry()
        
        result = await registry.execute("nonexistent_tool")
        
        assert result.success is False
        assert result.status == ExecutionStatus.NOT_FOUND
        assert "not found" in result.error.lower()
